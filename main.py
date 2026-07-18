import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    CallbackQueryHandler,
    filters
)
from groq import Groq
from resume_handler import resume_command, handle_resume_text
# Sahi functions ko import kar rahe hain ab:
from photo_handler import photo_receive, photo_callback_handler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hello! Main aapka AI Assistant hoon.\n\n"
        "✨ Naye features use karne ke liye ye commands try karein:\n"
        "📝 /resume - AI Professional Resume banane ke liye\n"
        "📄 /pdf - PDF aur Image tools (Image to PDF, Word, Resize) ke liye"
    )

async def pdf_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🖼️ Image to PDF", callback_data="img_to_pdf")],
        [InlineKeyboardButton("📝 Image to Word", callback_data="img_to_word")],
        [InlineKeyboardButton("📐 Resize PDF", callback_data="resize_pdf")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Niche diye gaye options me se select karein ki aap kya karna chahte hain:",
        reply_markup=reply_markup
    )

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    # Check agar click photo editing menu se aaya hai
    if query.data.startswith('edit_'):
        await photo_callback_handler(update, context)
        return
    
    context.user_data['pdf_action'] = query.data
    if query.data == "img_to_pdf":
        await query.edit_message_text("Aapne **Image to PDF** select kiya hai. Ab please wo Image send karein jise PDF banana hai.")
    elif query.data == "img_to_word":
        await query.edit_message_text("Aapne **Image to Word** select kiya hai. Ab please wo Image send karein jise Word doc me badalna hai.")
    elif query.data == "resize_pdf":
        await query.edit_message_text("Aapne **Resize PDF** select kiya hai. Ab please wo PDF file send karein jise resize karna hai.")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('state') == 'AWAITING_RESUME_DETAILS':
        await handle_resume_text(update, context)
        return

    user_text = update.message.text
    try:
        completion = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": user_text}]
        )
        bot_response = completion.choices[0].message.content
        await update.message.reply_text(bot_response)
    except Exception as e:
        logging.error(f"Groq API Error: {e}")
        await update.message.reply_text("Sorry, mujhe response generate karne me dikkat ho rahi hai.")

def main():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN environment variable nahi mila!")

    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("resume", resume_command))
    app.add_handler(CommandHandler("pdf", pdf_menu))
    
    # Ye click handlers ko filter karega aur sambhalega
    app.add_handler(CallbackQueryHandler(button_click))

    # Photo aane par photo_receive call hoga
    app.add_handler(MessageHandler(filters.PHOTO, photo_receive))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    print("Bot starting...")
    app.run_polling()

if __name__ == '__main__':
    main()
