import os
import telebot
from telebot.types import Update
from flask import Flask, request
import openai

# Настройки
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
ASSISTANT_ID = os.environ.get("ASSISTANT_ID")
RENDER_EXTERNAL_URL = os.environ.get("RENDER_EXTERNAL_URL")

bot = telebot.TeleBot(TELEGRAM_TOKEN)
openai.api_key = OPENAI_API_KEY

app = Flask(__name__)

# Установка webhook при запуске
@app.before_first_request
def set_webhook():
    bot.remove_webhook()
    webhook_url = RENDER_EXTERNAL_URL
    if webhook_url:
        bot.set_webhook(url=webhook_url)
        print(f"Setting webhook to: {webhook_url}")
    else:
        print("Webhook URL not provided in environment variables.")

# Обработка входящих запросов от Telegram
@app.route('/', methods=["POST"])
def webhook():
    json_str = request.get_data().decode("utf-8")
    update = Update.de_json(json_str)
    bot.process_new_updates([update])
    return "!", 200

# Обработка текстовых сообщений
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
        print("Ошибка при обращении к OpenAI:", e)

# Проверка сервера
@app.route('/', methods=["GET"])
def index():
    return "Bot is running", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
