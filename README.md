```markdown
# 🧠 Game Dialogue System

**Модуль диалоговой системы с поддержкой персонажей, локаций, лора и генерацией реплик через локальную LLaMA 3.**

![FastAPI + React + PostgreSQL + LLaMA](https://img.shields.io/badge/stack-FastAPI%20%7C%20React%20%7C%20PostgreSQL%20%7C%20llama3-brightgreen)

---

## 📌 Возможности

- ✨ Визуальный интерфейс для создания персонажей, локаций и лора
- 🧑‍🤝‍🧑 Диалог с любым созданным NPC
- 📂 Хранение всей информации в PostgreSQL
- 🦙 Генерация ответов через локальную модель LLaMA 3 (Ollama)
- 🧱 Полностью контейнеризировано (Docker + Docker Compose)
- 🧩 OpenAPI-документация доступна по `/api/docs`

---

## ⚙️ Архитектура

```

React SPA (Vite)
⬇
Nginx (SPA + /api → FastAPI)
⬇
FastAPI (REST API, логика диалога)
⬇
PostgreSQL (данные)
⬇
LLaMA 3 (через Ollama, локально)

```

---

## 🗃 Структура проекта

```

project-root/
├── backend/           # FastAPI (Python)
│   ├── app/
│   │   ├── main.py, models.py, database.py ...
│   └── Dockerfile
├── frontend/          # React + Vite
│   ├── src/
│   ├── nginx.conf
│   └── Dockerfile
├── .env               # Переменные окружения
├── docker-compose.yml
└── README.md

````

---

## 🚀 Быстрый запуск (локально с Docker)

> Подходит для **Windows / Linux / macOS**, требуется только **Docker Desktop**.

### 🐋 Установка Docker:

- [Docker Desktop для Windows](https://docs.docker.com/desktop/install/windows-install/)
- [Docker для Linux](https://docs.docker.com/engine/install/)

### 🦙 Установка Ollama (LLaMA 3):

1. Установи Ollama:
   [https://ollama.com/download](https://ollama.com/download)

2. Запусти в терминале:
   ```bash
   ollama run llama3
````

Это скачает и запустит модель локально (доступна по `http://localhost:11434`).

---

### 📦 Запуск проекта:

1. Клонируй проект:

   ```bash
   git clone git@github.com:DyudinDaniil/dialog_system.git
   cd game-dialogue-system
   ```

2. Убедись, что файл `.env` присутствует (см. ниже).

3. Запусти проект:

   ```bash
   docker compose up --build
   ```

4. Открой браузер:

   * Фронтенд: [http://localhost](http://localhost)
   * API-документация: [http://localhost/api/docs](http://localhost/api/docs)

---

## 📄 .env файл (пример)

Создай в корне `.env`:

```env
POSTGRES_USER=fastapi_user
POSTGRES_PASSWORD=fastapi_pass
POSTGRES_DB=fastapi_db
POSTGRES_HOST=db
POSTGRES_PORT=5432

OLLAMA_URL=http://host.docker.internal:11434/api/generate
LLAMA_MODEL=llama3

REACT_APP_API_BASE=/api
```

---

## 🛠 Что реализовано

| Раздел                 | Описание                                                                |
| ---------------------- | ----------------------------------------------------------------------- |
| Персонажи (Characters) | Создание, обновление, удаление, список, выбор для диалога               |
| Локации (Locations)    | Название, описание, точки интереса, список NPC                          |
| Лор (Lore)             | Общий контекст фэнтезийного мира                                        |
| Диалоговая система     | Игрок выбирает локацию → NPC → ведёт диалог через интерфейс             |
| Генерация реплик       | Ответы NPC создаются LLaMA 3 (Ollama API) на основе контекста и вопроса |

---

## 🧼 Git-игнорирование

Файл `.env` и временные файлы не попадают в репозиторий. В `.gitignore` уже указано:

```gitignore
.env
node_modules/
__pycache__/
frontend/dist/
.venv/
.idea/
```

