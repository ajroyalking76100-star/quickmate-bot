import os
import logging
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
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
from photo_handler import photo_receive, photo_callback_handler

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Initialize Groq client
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hello! Main aapka AI Assistant hoon.\n\n"
        "✨ Naye features use karne ke liye ye commands try karein:\n"
        "📝 /resume - AI Professional Resume banane ke liye\n"
        "📄 /pdf - PDF aur Image tools (Image to PDF, Word, Resize) ke liye"
    )

# /pdf command menu
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

# Handle button clicks
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    # Check if click is from photo editing menu
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

# /resume command handler
async def resume_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['state'] = 'AWAITING_RESUME_DETAILS'
    instruction_text = (
        "📝 **AI Professional Resume Builder** 📝\n\n"
        "Apna resume banane ke liye niche diye gaye format ko copy karein, apni details fill karein aur mujhe send karein:\n\n"
        "NAME: Aapka Naam\n"
        "EMAIL: aapkaemail@example.com\n"
        "PHONE: +91 9876543210\n"
        "SUMMARY: Apne baare me ek chhota professional summary.\n"
        "EXPERIENCE: Aapka work experience details.\n"
        "EDUCATION: Aapki padhai ki details.\n"
        "SKILLS: Aapki skills (jaise Python, Excel, wagerah)."
    )
    await update.message.reply_text(instruction_text)

# Resume PDF generator helper
async def handle_resume_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    chat_id = update.message.chat_id
    
    details = {}
    lines = text.split('\n')
    for line in lines:
        if ':' in line:
            key, val = line.split(':', 1)
            details[key.strip().upper()] = val.strip()
            
    name = details.get('NAME', 'Resume')
    email = details.get('EMAIL', 'N/A')
    phone = details.get('PHONE', 'N/A')
    summary = details.get('SUMMARY', 'N/A')
    exp = details.get('EXPERIENCE', 'N/A')
    edu = details.get('EDUCATION', 'N/A')
    skills = details.get('SKILLS', 'N/A')
    
    filename = f"resume_{chat_id}.pdf"
    doc = SimpleDocTemplate(filename, pagesize=letter, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
    story = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=24, spaceAfter=10)
    heading_style = ParagraphStyle('HeadingStyle', parent=styles['Heading2'], fontSize=14, spaceBefore=10, spaceAfter=5)
    body_style = ParagraphStyle('BodyStyle', parent=styles['Normal'], fontSize=10, spaceAfter=5)
    
    story.append(Paragraph(name, title_style))
    story.append(Paragraph(f"Email: {email} | Phone: {phone}", body_style))
    story.append(Spacer(1, 15))
    
    story.append(Paragraph("Professional Summary", heading_style))
    story.append(Paragraph(summary, body_style))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("Work Experience", heading_style))
    story.append(Paragraph(exp, body_style))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("Education", heading_style))
    story.append(Paragraph(edu, body_style))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("Skills", heading_style))
    story.append(Paragraph(skills, body_style))
    
    try:
        doc.build(story)
        with open(filename, 'rb') as pdf_file:
            await update.message.reply_document(document=pdf_file, filename=f"{name}_Resume.pdf", caption="Ye raha aapka AI Generated Resume! 🚀")
        os.remove(filename)
    except Exception as e:
        logging.error(f"PDF Generation Error: {e}")
        await update.message.reply_text("Sorry, resume PDF generate karne me koi error aayi.")
        
    context.user_data['state'] = None

# Chat text handling with Groq AI
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
    
    app.add_handler(CallbackQueryHandler(button_click))
    app.add_handler(MessageHandler(filters.PHOTO, photo_receive))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    print("Bot starting...")
    app.run_polling()

if __name__ == '__main__':
    main()
