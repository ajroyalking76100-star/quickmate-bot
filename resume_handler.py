import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

async def create_resume(update, context):
    await update.message.reply_text(
        "📝 *Resume Generator*\n\n"
        "Apni details is format me bhejein:\n"
        "NAME: Aapka Naam\n"
        "EMAIL: abc@email.com\n"
        "PHONE: 9876543210\n"
        "SKILLS: Python, SQL, Git\n"
        "EXPERIENCE: 2 Years at XYZ Company", 
        parse_mode="Markdown"
    )

async def generate_resume_pdf(update, context):
    text = update.message.text
    lines = text.split('\n')
    data = {}
    
    for line in lines:
        if ':' in line:
            k, v = line.split(':', 1)
            data[k.strip().upper()] = v.strip()
    
    if "NAME" not in data:
        return False # Format sahi nahi hai, normal AI handle karega

    pdf_filename = f"Resume_{data.get('NAME', 'User')}.pdf"
    doc = SimpleDocTemplate(pdf_filename, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    story = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=24, textColor=colors.HexColor("#1A365D"), spaceAfter=10)
    normal_style = ParagraphStyle('Normal', parent=styles['Normal'], fontSize=11, leading=14, spaceAfter=8)
    heading_style = ParagraphStyle('Heading', parent=styles['Heading2'], fontSize=14, textColor=colors.HexColor("#2B6CB0"), spaceBefore=10, spaceAfter=5)

    story.append(Paragraph(data.get("NAME", "RESUME"), title_style))
    story.append(Paragraph(f"<b>Email:</b> {data.get('EMAIL', '-') if data.get('EMAIL') else '-'} | <b>Phone:</b> {data.get('PHONE', '-') if data.get('PHONE') else '-'}", normal_style))
    story.append(Spacer(1, 10))
    
    if "SKILLS" in data:
        story.append(Paragraph("Skills", heading_style))
        story.append(Paragraph(data["SKILLS"], normal_style))
        
    if "EXPERIENCE" in data:
        story.append(Paragraph("Experience", heading_style))
        story.append(Paragraph(data["EXPERIENCE"], normal_style))

    doc.build(story)
    
    with open(pdf_filename, 'rb') as pdf:
        await update.message.reply_document(document=pdf, filename=pdf_filename, caption="Ye lijiye aapka generated Resume! 📄")
    
    os.remove(pdf_filename)
    return True

