import os
import telebot
from flask import Flask, request
import openai

# Читаем переменные окружения
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID = os.getenv("ASSISTANT_ID")
RENDER_EXTERNAL_URL = os.getenv("RENDER_EXTERNAL_URL")

bot = telebot.TeleBot(BOT_TOKEN)
openai.api_key = OPENAI_API_KEY

app = Flask(__name__)

# Установка webhook
@app.route("/", methods=["GET"])
def index():
    return "🤖 Bot is running"

@app.route("/", methods=["POST"])
def webhook():
    json_data = request.get_json()
    if json_data:
        bot.process_new_updates([telebot.types.Update.de_json(json_data)])
    return "ok", 200

# Логика ответа ассистента
@bot.message_handler(func=lambda message: True, content_types=['text'])
def handle_message(message):
    user_input = message.text
    user_id = f"telegram-{message.from_user.id}"

    try:
        response = openai.beta.assistants.chat.completions.create(
            assistant_id=ASSISTANT_ID,
            model="gpt-4o",
            messages=[{"role": "user", "content": user_input}],
            user=user_id
        )
        reply_text = response.choices[0].message.content.strip()
        bot.reply_to(message, reply_text)
    except Exception as e:
        print("❌ OpenAI API ERROR:", str(e))
        bot.reply_to(message, f"⚠️ Ошибка при обращении к ИИ:\n{e}")

# Устанавливаем Webhook при запуске
if __name__ == "__main__":
    webhook_url = f"{RENDER_EXTERNAL_URL}"
    print(f"Setting webhook to: {webhook_url}")
    bot.remove_webhook()
    bot.set_webhook(url=webhook_url)
    app.run(host="0.0.0.0", port=10000)
