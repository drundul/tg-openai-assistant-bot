import os
import telebot
from flask import Flask, request
import openai

# Переменные окружения
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID = os.getenv("ASSISTANT_ID")
RENDER_EXTERNAL_URL = os.getenv("RENDER_EXTERNAL_URL")

bot = telebot.TeleBot(BOT_TOKEN)
openai.api_key = OPENAI_API_KEY
app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return "🤖 Bot is running"

@app.route("/", methods=["POST"])
def webhook():
    json_data = request.get_json()
    if json_data:
        bot.process_new_updates([telebot.types.Update.de_json(json_data)])
    return "ok", 200

@bot.message_handler(func=lambda message: True, content_types=['text'])
def handle_message(message):
    user_input = message.text
    user_id = f"telegram-{message.from_user.id}"

    try:
        # Шаг 1: создаём Thread
        thread = openai.beta.threads.create()

        # Шаг 2: отправляем сообщение в Thread
        openai.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_input
        )

        # Шаг 3: запускаем Assistant
        run = openai.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=ASSISTANT_ID
        )

        # Шаг 4: ждём завершения выполнения
        import time
        while True:
            run_status = openai.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
            if run_status.status == "completed":
                break
            elif run_status.status == "failed":
                raise Exception("⚠️ Run failed.")
            time.sleep(1)

        # Шаг 5: получаем ответ
        messages = openai.beta.threads.messages.list(thread_id=thread.id)
        reply = next(
            (msg.content[0].text.value for msg in reversed(messages.data) if msg.role == "assistant"),
            "❓ Нет ответа от ассистента."
        )

        bot.reply_to(message, reply)

    except Exception as e:
        print("❌ Ошибка:", e)
        bot.reply_to(message, f"⚠️ Ошибка при обращении к ИИ:\n{e}")

# Устанавливаем webhook
if __name__ == "__main__":
    print(f"Setting webhook to: {RENDER_EXTERNAL_URL}")
    bot.remove_webhook()
    bot.set_webhook(url=RENDER_EXTERNAL_URL)
    app.run(host="0.0.0.0", port=10000)
