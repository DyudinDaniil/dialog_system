import os, requests

# Адрес Ollama API – используем host.docker.internal (Docker Desktop) и порт 11434
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://host.docker.internal:11434/api/generate")
LLAMA_MODEL = os.getenv("LLAMA_MODEL", "llama3")  # имя модели для Ollama

def generate_npc_reply(prompt: str) -> str:
    """
    Отправляет промпт в Ollama API и возвращает сгенерированный ответ модели.
    """
    payload = {
        "model": LLAMA_MODEL,
        "prompt": prompt,
        "stream": False  # отключаем поток, чтобы получить полный ответ в JSON
    }
    try:
        res = requests.post(OLLAMA_URL, json=payload, timeout=30)
        res.raise_for_status()
    except Exception as e:
        print(f"LLM request failed: {e}")
        # В случае ошибки можно вернуть шаблонный ответ
        return "Извините, я сейчас не могу ответить."
    data = res.json()
    # Ollama возвращает JSON со списком частей, либо объект. При stream=False ожидаем один объект с 'response'
    # Согласно документации, ответ может быть вида {"model": ..., "created_at": ..., "response": "text", ...}
    reply_text = ""
    if isinstance(data, list):
        # Если на всякий случай получили список (стрим), склеим content полей
        reply_text = "".join(item.get("response", "") for item in data)
    else:
        reply_text = data.get("response", "")
    # Убираем лишние переводы строк или маркеры, если модель их добавляет
    return reply_text.strip()
