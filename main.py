from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, ContextTypes, filters
import requests
import os
from threading import Thread
from http.server import BaseHTTPRequestHandler, HTTPServer

class WebhookServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), WebhookServer)
    print(f"Web server started on port {port}")
    server.serve_forever()

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "8837315359:AAEB29lySLlJLnf7XJgFUIuaZqkC8ICQjDU")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "Gsk_NAGzJyOdRmmBXGh3zNd2WGdyb3FYWaYBImNw3Nsn50Pj4a9QfzXy")

GROQ_MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "mixtral-8x7b-32768"
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 QuickMate AI Cloud me active hai!")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    bot_response = None
    for model_name in GROQ_MODELS:
        payload = {
            "model": model_name,
            "messages": [{"role": "user", "content": user_text}]
        }
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=12)
            if response.status_code == 200:
                data = response.json()
                bot_response = data['choices'][0]['message']['content']
                break
        except Exception:
            continue

    if bot_response:
        await update.message.reply_text(bot_response)
    else:
        await update.message.reply_text("⚠️ Groq API temporary busy hai.")

if __name__ == "__main__":
    Thread(target=run_web_server, daemon=True).start()
    
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
    
    print("Bot is polling...")
    app.run_polling()
