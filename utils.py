import json

def load_messages():
    with open("messages.json", "r", encoding="utf-8") as file:
        return json.load(file)

messages = load_messages()

def get_message(key):
    return messages.get(key, "Повідомлення не знайдено 😕")