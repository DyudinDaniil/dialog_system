FROM python:3.12-slim

# Установим рабочую директорию
WORKDIR /app

# Установим зависимости
COPY requirements.txt .
RUN pip install -r requirements.txt

# Копируем исходный код
COPY app ./app

# Указываем порт
EXPOSE 8000

# Запускаем uvicorn-сервер при старте контейнера
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

