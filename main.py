import os
import logging
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from telegram import Update
from telegram.ext import ContextTypes

# Function to handle /resume command
async def resume_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Set state to wait for user text input
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
    await update.message.reply_text(instruction_text, parse_mode="Markdown")

# Function to handle the details text and generate PDF
async def handle_resume_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    chat_id = update.message.chat_id
    
    # Simple parsing logic
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
    
    # PDF generation setup
    filename = f"resume_{chat_id}.pdf"
    doc = SimpleDocTemplate(filename, pagesize=letter, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
    story = []
    
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=24, spaceAfter=10)
    heading_style = ParagraphStyle('HeadingStyle', parent=styles['Heading2'], fontSize=14, spaceBefore=10, spaceAfter=5)
    body_style = ParagraphStyle('BodyStyle', parent=styles['Normal'], fontSize=10, spaceAfter=5)
    
    # Build PDF Content
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
        
        # Send PDF file to user
        with open(filename, 'rb') as pdf_file:
            await update.message.reply_document(document=pdf_file, filename=f"{name}_Resume.pdf", caption="Ye raha aapka AI Generated Professional Resume! 🚀")
            
        # Clean up file from server
        os.remove(filename)
    except Exception as e:
        logging.error(f"PDF Generation Error: {e}")
        await update.message.reply_text("Sorry, resume PDF generate karne me koi error aayi.")
        
    # Reset state
    context.user_data['state'] = None
