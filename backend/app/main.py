from typing import List
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import requests
from . import models, schemas
from .database import SessionLocal, engine
from .llm import generate_npc_reply  # функция вызова модели Ollama (опишем ниже)

# Инициализируем таблицы
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI NPC Dialogue API")

# Разрешаем CORS для фронтенда (React dev server на localhost:3000, и для безопасности можно указать адрес)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # лучше указать конкретно "http://localhost:3000"
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Зависимость для получения сессии БД в каждом запросе
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---- ЭНДПОИНТЫ Characters ----

@app.post("/characters", response_model=schemas.CharacterRead)
def create_character(char: schemas.CharacterCreate, db: Session = Depends(get_db)):
    # Проверка: уникальность имени или другие бизнес-правила можно добавить
    new_char = models.Character(**char.dict())
    db.add(new_char)
    db.commit()
    db.refresh(new_char)  # получить сгенерированный id
    return new_char

@app.get("/characters", response_model=List[schemas.CharacterRead])
def list_characters(db: Session = Depends(get_db)):
    return db.query(models.Character).all()

@app.get("/characters/{char_id}", response_model=schemas.CharacterRead)
def get_character(char_id: int, db: Session = Depends(get_db)):
    char = db.query(models.Character).get(char_id)
    if not char:
        raise HTTPException(status_code=404, detail="Character not found")
    return char

@app.patch("/characters/{char_id}", response_model=schemas.CharacterRead)
def update_character(char_id: int, updates: schemas.CharacterUpdate, db: Session = Depends(get_db)):
    char = db.query(models.Character).get(char_id)
    if not char:
        raise HTTPException(status_code=404, detail="Character not found")
    update_data = updates.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(char, field, value)
    db.commit()
    db.refresh(char)
    return char

@app.delete("/characters/{char_id}")
def delete_character(char_id: int, db: Session = Depends(get_db)):
    char = db.query(models.Character).get(char_id)
    if not char:
        raise HTTPException(status_code=404, detail="Character not found")
    db.delete(char)
    db.commit()
    return {"detail": "Character deleted successfully"}

# ---- ЭНДПОИНТЫ Locations ----

@app.post("/locations", response_model=schemas.LocationRead)
def create_location(loc: schemas.LocationCreate, db: Session = Depends(get_db)):
    new_loc = models.Location(**loc.dict())
    db.add(new_loc)
    db.commit()
    db.refresh(new_loc)
    return new_loc

@app.get("/locations", response_model=List[schemas.LocationRead])
def list_locations(db: Session = Depends(get_db)):
    return db.query(models.Location).all()

@app.get("/locations/{loc_id}", response_model=schemas.LocationRead)
def get_location(loc_id: int, db: Session = Depends(get_db)):
    loc = db.query(models.Location).get(loc_id)
    if not loc:
        raise HTTPException(status_code=404, detail="Location not found")
    return loc

@app.patch("/locations/{loc_id}", response_model=schemas.LocationRead)
def update_location(loc_id: int, updates: schemas.LocationUpdate, db: Session = Depends(get_db)):
    loc = db.query(models.Location).get(loc_id)
    if not loc:
        raise HTTPException(status_code=404, detail="Location not found")
    # Обновляем только указанные поля
    for field, value in updates.dict(exclude_unset=True).items():
        setattr(loc, field, value)
    db.commit()
    db.refresh(loc)
    return loc

@app.delete("/locations/{loc_id}")
def delete_location(loc_id: int, db: Session = Depends(get_db)):
    loc = db.query(models.Location).get(loc_id)
    if not loc:
        raise HTTPException(status_code=404, detail="Location not found")
    db.delete(loc)
    db.commit()
    return {"detail": "Location deleted successfully"}

# ---- ЭНДПОИНТЫ Lore (глобальный лор) ----

@app.get("/lore", response_model=schemas.LoreRead)
def get_lore(db: Session = Depends(get_db)):
    lore = db.query(models.Lore).first()
    if lore:
        return {"content": lore.content or ""}
    else:
        # Если записи еще нет, вернем пустой контент
        return {"content": ""}

@app.put("/lore", response_model=schemas.LoreRead)
def update_lore(update: schemas.LoreUpdate, db: Session = Depends(get_db)):
    lore = db.query(models.Lore).first()
    if not lore:
        # Если записи нет, создадим ее
        lore = models.Lore(content=update.content)
        db.add(lore)
    else:
        lore.content = update.content
    db.commit()
    return {"content": lore.content}

# ---- ЭНДПОИНТЫ Диалога ----

@app.post("/dialogue", response_model=schemas.DialogueResponse)
def send_message(character_id: int, location_id: int, message: str, db: Session = Depends(get_db)):
    # Найдем соответствующего персонажа и локацию (для валидации и контекста)
    char = db.query(models.Character).get(character_id)
    loc = db.query(models.Location).get(location_id)
    if not char or not loc:
        raise HTTPException(status_code=404, detail="Character or location not found")
    # Сохраняем сообщение пользователя в историю
    user_msg = models.Dialogue(character_id=character_id, role="user", message=message)
    db.add(user_msg)
    db.commit()
    # Получаем всю историю предыдущих сообщений этого NPC
    history = db.query(models.Dialogue).filter_by(character_id=character_id).order_by(models.Dialogue.timestamp).all()
    # Формируем промпт для LLM на основе лора, локации, NPC, истории
    prompt = _build_prompt(lore=db.query(models.Lore).first(), location=loc, character=char, history=history, user_message=message)
    # Вызываем модель LLM через Ollama API
    ai_reply_text = generate_npc_reply(prompt)
    # Сохраняем ответ модели в БД
    ai_msg = models.Dialogue(character_id=character_id, role="assistant", message=ai_reply_text)
    db.add(ai_msg)
    db.commit()
    return {"reply": ai_reply_text}

@app.get("/dialogue/{character_id}", response_model=List[schemas.DialogueMessageRead])
def get_dialogue_history(character_id: int, db: Session = Depends(get_db)):
    messages = db.query(models.Dialogue).filter_by(character_id=character_id).order_by(models.Dialogue.timestamp).all()
    return messages

# Вспомогательная функция для построения контекста промпта:
def _build_prompt(lore, location, character, history, user_message):
    # Текст глобального лора
    lore_text = lore.content if lore else ""
    # Описание локации
    loc_desc = location.description or ""
    # Если выбрана конкретная "репутация" (предположим, первый уровень по индексу для примера),
    # добавим описание этого уровня репутации, иначе пусто
    rep_text = ""
    if location.reputation_levels:
        # допустим, используем первый уровень как текущий (или выбираемый параметр можно тоже передавать)
        rep_text = location.reputation_levels[0]  # упрощение: берём 0-й как выбранный
    # Характеристики NPC
    npc_desc = (f"{character.name}, {character.age}-летний {character.sex}, "
                f"черты: {', '.join(character.traits or [])}. "
                f"Отношение к игроку: {character.attitude or 'неизвестно'}.")
    # История предыдущих реплик (кроме последнего пользовательского, которое мы отдельно передадим?)
    history_lines = ""
    for msg in history:
        role = "Игрок" if msg.role == "user" else character.name
        history_lines += f"{role}: {msg.message}\n"
    # Финальный промпт, объединяем все части:
    prompt = (f"Глобальный лор:\n{lore_text}\n\n"
              f"Локация: {location.name}. {loc_desc}\n"
              f"Репутация игрока: {rep_text}\n\n"
              f"Персонаж: {npc_desc}\n\n"
              f"История диалога:\n{history_lines}\n"
              f"Игрок: {user_message}\nПерсонаж:")
    return prompt
