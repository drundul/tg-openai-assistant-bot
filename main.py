import os
import telebot
from telebot.types import Update
from flask import Flask, request
import openai

# Переменные окружения
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
ASSISTANT_ID = os.environ.get("ASSISTANT_ID")
RENDER_EXTERNAL_URL = os.environ.get("RENDER_EXTERNAL_URL")

bot = telebot.TeleBot(TELEGRAM_TOKEN)
openai.api_key = OPENAI_API_KEY

app = Flask(__name__)

# Webhook установка (прямо при запуске)
def set_webhook():
    bot.remove_webhook()
    if RENDER_EXTERNAL_URL:
        bot.set_webhook(url=RENDER_EXTERNAL_URL)
        print(f"Webhook set to: {RENDER_EXTERNAL_URL}")
    else:
        print("No RENDER_EXTERNAL_URL provided!")

set_webhook()  # Вызов при старте

# Обработка входящих сообщений от Telegram
@app.route('/', methods=["POST"])
def webhook():
    json_str = request.get_data().decode("utf-8")
    update = Update.de_json(json_str)
    bot.process_new_updates([update])
    return "!", 200

# Ответы на текстовые сообщения
@bot.message_handler(func=lambda message: True, content_types=['text'])
def handle_message(message):
    user_input = message.text
    user_id = f"telegram-{message.from_user.id}"

    try:
        response = openai.beta.assistants.chat.completions.create(
            assistant_id=ASSISTANT_ID,
            model="gpt-4o",
            messages=[
                {"role": "user", "content": user_input}
            ],
            user=user_id
        )

        reply_text = response.choices[0].message.content.strip()
        bot.reply_to(message, reply_text)

    except Exception as e:
        bot.reply_to(message, "Произошла ошибка при обращении к ИИ.")
        print("OpenAI error:", e)

# Проверка сервера (GET-запрос)
@app.route('/', methods=["GET"])
def index():
    return "Bot is running", 200

# Запуск сервера
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
