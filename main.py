import os
import asyncio
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, ContextTypes, filters
import requests
from aiohttp import web

# Tokens jo aapne Environment Variables me set kiye hain
BOT_TOKEN = os.environ.get("8837315359:AAEB29lySLlJLnf7XJgFUIuaZqkC8ICQjDU")
GROQ_API_KEY = os.environ.get("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")

GROQ_MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "mixtral-8x7b-32768"
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 QuickMate AI successfully live ho chuka hai! Puchiye kya puchna hai.")

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
        await update.message.reply_text("⚠️ Groq ke backup models abhi temporary busy hain. Kripya ek baar fir se try karein.")

# Render ko khush rakhne ke liye simple web handler
async def handle_web(request):
    return web.Response(text="QuickMate AI is Active and Running!")

async def main():
    # 1. Web server setup Render ke port ke liye
    app_web = web.Application()
    app_web.router.add_get('/', handle_web)
    runner = web.AppRunner(app_web)
    await runner.setup()
    
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"Web server started on port {port}")

    # 2. Telegram Bot setup
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    # Dono ko ek sath loop me run karne ke liye safe method
    async with application:
        await application.initialize()
        await application.start()
        print("Bot polling initiated...")
        await application.updater.start_polling()
        
        # Keep running infinitely loop
        while True:
            await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())
