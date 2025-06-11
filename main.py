import os
import telebot
import openai
from flask import Flask, request
from telebot.types import Update

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID = os.getenv("ASSISTANT_ID")
WEBHOOK_URL = os.getenv("RENDER_EXTERNAL_URL")

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
app = Flask(__name__)

openai.api_key = OPENAI_API_KEY

@app.route(f'/{TELEGRAM_BOT_TOKEN}', methods=['POST'])
def webhook():
    json_str = request.stream.read().decode("UTF-8")
    update = Update.de_json(json_str)
    bot.process_new_updates([update])
    return '', 200

@app.route('/')
def index():
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL + f'{TELEGRAM_BOT_TOKEN}')
    return "Webhook set", 200

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_input = message.text
    thread = openai.beta.threads.create()
    openai.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=user_input
    )
    run = openai.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=ASSISTANT_ID
    )
    import time
    while True:
        run_status = openai.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
        if run_status.status == "completed":
            break
        time.sleep(1)
    messages = openai.beta.threads.messages.list(thread_id=thread.id)
    content = messages.data[0].content[0].text.value
    bot.send_message(message.chat.id, content)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))