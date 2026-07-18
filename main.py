import os
import threading
import http.server
import socketserver
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from groq import Groq

# 1. Environment Variables loading
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_KEY = os.getenv("GROQ_API_KEY")

# 2. Port Binding for Render
PORT = int(os.getenv("PORT", 8080))

def run_health_server():
    class HealthHandler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"Bot is alive!")

    with socketserver.TCPServer(("", PORT), HealthHandler) as httpd:
        print(f"Serving health check on port {PORT}")
        httpd.serve_forever()

# Start the health check web server in a background thread
threading.Thread(target=run_health_server, daemon=True).start()

# 3. Initialize Groq Client
groq_client = Groq(api_key=GROQ_KEY)

# 4. Telegram Bot Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! Main aapka AI assistant hoon. Boliye, kya madad karoon?")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    try:
        completion = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": user_text}]
        )
        reply = completion.choices[0].message.content
        await update.message.reply_text(reply)
    except Exception as e:
        await update.message.reply_text("Sorry, abhi main reply nahi kar pa raha hoon.")
        print(f"Groq Error: {e}")

def main():
    if not TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN environment variable missing!")
        
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot is starting polling...")
    application.run_polling()

if __name__ == "__main__":
    main()
