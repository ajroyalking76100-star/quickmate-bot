import os
import threading
from http.server import SimpleHTTPRequestHandler, HTTPServer
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, ContextTypes, filters
import requests

# Render ke Environment Variables se automatic utha lega (Safe and Secure)
BOT_TOKEN = os.environ.get("8837315359:AAEB29lySLlJLnf7XJgFUIuaZqkC8ICQjDU")
GROQ_API_KEY = os.environ.get("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")

GROQ_MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "mixtral-8x7b-32768"
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 QuickMate AI live ho chuka hai! Puchiye kya puchna hai.")

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
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            if response.status_code == 200:
                data = response.json()
                bot_response = data['choices'][0]['message']['content']
                break
        except Exception:
            continue

    if bot_response:
        await update.message.reply_text(bot_response)
    else:
        await update.message.reply_text("⚠️ Groq models abhi busy hain. Kripya thodi der baad try karein.")

# Render ka Port handle karne ke liye simple aur lightweight Web Server
def run_health_server():
    port = int(os.environ.get("PORT", 8080))
    server_address = ('', port)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    print(f"Web server active on port {port}")
    httpd.serve_forever()

if __name__ == "__main__":
    # Web server ko background thread me chalayein taaki Render port crash na kare
    t = threading.Thread(target=run_health_server, daemon=True)
    t.start()

    # Telegram Bot ki official standard polling chalu karein
    print("Starting bot polling...")
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
    
    application.run_polling()
