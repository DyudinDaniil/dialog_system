import os
import requests
from typing import Optional
import json


# Класс для загрузки лора игры (без изменений)
class GameWorld:
    def __init__(self, lore_file_path: str):
        self.lore = self._load_lore(lore_file_path)

    def _load_lore(self, path: str) -> str:
        with open(path, 'r', encoding='utf-8') as file:
            return file.read().strip()


# Основной класс диалоговой системы (с API!)
class DialogueSystem:
    def __init__(self, lore_file: str):
        self.world = GameWorld(lore_file)
        self.context = (
            f"Ты — NPC в игре. Отвечай кратко (1-2 предложения) и в контексте мира:\n"
            f"{self.world.lore}\n\n"
            "Текущий диалог:\n"
        )

    def start_chat(self):
        print("Диалоговая система запущена. Напиши 'стоп' чтобы выйти.\n")
        while True:
            user_input = input("Игрок: ")
            if user_input.lower() == "стоп":
                break

            prompt = f"{self.context}Игрок: {user_input}\nNPC:"
            response = self.generate_response(prompt)  # Теперь здесь работает API

            print(f"NPC: {response}\n")
            self.context += f"Игрок: {user_input}\nNPC: {response}\n"

    # === Вставка из пункта 3 ===
    def generate_response(self, prompt: str) -> str:
        api_url = "http://localhost:11434/api/chat"  # Ollama API
        headers = {"Content-Type": "application/json"}
        payload = {
            "model": "llama3",  # Или другая модель (mistral, phi3)
            "messages": [
                {"role": "system", "content": f"Ты NPC в игре. Отвечай кратко в контексте: {self.world.lore}"},
                {"role": "user", "content": prompt}
            ],
            "stream": False,
            "options": {"temperature": 0.7}
        }

        try:
            response = requests.post(api_url, json=payload, headers=headers)
            if response.status_code == 200:
                return response.json()["message"]["content"]
            else:
                return f"Ошибка: {response.text}"
        except Exception as e:
            return f"Ошибка API: {e}"

    # Запуск системы
if __name__ == "__main__":
    system = DialogueSystem("game_lore.txt")
    system.start_chat()