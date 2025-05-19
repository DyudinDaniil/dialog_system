from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# ---- Схемы для Character ----
class CharacterBase(BaseModel):
    name: str
    age: Optional[int] = None
    sex: Optional[str] = None
    traits: Optional[List[str]] = None    # список черт характера
    attitude: Optional[str] = None
    location_id: int                      # ссылка на локацию персонажа

class CharacterCreate(CharacterBase):
    pass  # те же поля, что и CharacterBase

class CharacterUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    sex: Optional[str] = None
    traits: Optional[List[str]] = None
    attitude: Optional[str] = None
    location_id: Optional[int] = None

class CharacterRead(CharacterBase):
    id: int
    class Config:
        orm_mode = True  # позволяет напрямую возвращать объекты ORM через Pydantic

# ---- Схемы для Location ----
class LocationBase(BaseModel):
    name: str
    description: Optional[str] = None
    reputation_levels: Optional[List[str]] = None
    points_of_interest: Optional[List[str]] = None

class LocationCreate(LocationBase):
    pass

class LocationUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    reputation_levels: Optional[List[str]] = None
    points_of_interest: Optional[List[str]] = None

class LocationRead(LocationBase):
    id: int
    class Config:
        orm_mode = True

# ---- Схемы для Lore ----
class LoreRead(BaseModel):
    content: str

class LoreUpdate(BaseModel):
    content: str

# ---- Схема для сообщений диалога ----
class DialogueMessageRead(BaseModel):
    role: str       # "user" или "assistant"
    message: str
    timestamp: datetime
    class Config:
        orm_mode = True

# При необходимости можно добавить схему для ответа /dialogue (например, с полем reply)
class DialogueResponse(BaseModel):
    reply: str
