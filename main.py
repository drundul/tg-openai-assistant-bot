
import telebot
import os
from flask import Flask, request

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return 'Bot is running'

@app.route('/', methods=['POST'])  # ← изменено
def webhook():
    json_str = request.stream.read().decode("UTF-8")
    update = Update.de_json(json_str)
    bot.process_new_updates([update])
    return '', 200

if __name__ == '__main__':
    webhook_url = os.getenv("RENDER_EXTERNAL_URL")
    print(f"Setting webhook to: {webhook_url}")
    bot.remove_webhook()
    bot.set_webhook(url=webhook_url)
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
