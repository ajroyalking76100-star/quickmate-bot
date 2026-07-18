import os
import threading
import http.server
import socketserver
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from groq import Groq

# Naye modules ko import kiya
from resume_handler import create_resume, generate_resume_pdf
from photo_handler import photo_receive, photo_callback_handler

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
    await update.message.reply_text(
        "Hello! Main aapka AI assistant hoon. 🤖\n\n"
        "Aap mujhse chat kar sakte hain, /resume dabakar resume bana sakte hain, ya koi photo bhejkar use edit kar sakte hain!"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    
    # Check karien ki kahin user resume ki details toh nahi bhej raha
    if "NAME:" in user_text.upper():
        success = await generate_resume_pdf(update, context)
        if success:
            return

    # Normal AI Chat Functionality
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

    # Saare Handlers register karein
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("resume", create_resume))
    
    # Photo received handle karne ke liye
    application.add_handler(MessageHandler(filters.PHOTO, photo_receive))
    
    # Photo ke buttons click handle karne ke liye
    application.add_handler(CallbackQueryHandler(photo_callback_handler))
    
    # Normal text messages ke liye
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot is starting polling...")
    application.run_polling()

if __name__ == "__main__":
    main()
