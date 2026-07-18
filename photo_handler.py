import os
from PIL import Image, ImageFilter
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

async def photo_receive(update, context):
    photo_file = await update.message.photo[-1].get_file()
    file_path = f"user_photo_{update.message.from_user.id}.jpg"
    await photo_file.download_to_drive(file_path)
    context.user_data['photo_path'] = file_path

    keyboard = [
        [InlineKeyboardButton("⚫ Black & White", callback_data='edit_bw')],
        [InlineKeyboardButton("🌫️ Blur Effect", callback_data='edit_blur')],
        [InlineKeyboardButton("📐 Resize (Thumbnail)", callback_data='edit_resize')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Photo mil gayi! Aapko isme kya edit karna hai?", reply_markup=reply_markup)

async def photo_callback_handler(update, context):
    query = update.callback_query
    await query.answer()
    
    file_path = context.user_data.get('photo_path')
    if not file_path or not os.path.exists(file_path):
        await query.edit_message_text("Sorry, photo expire ho gayi hai. Kripya fir se bhejein.")
        return

    output_path = f"edited_{file_path}"
    img = Image.open(file_path)

    if query.data == 'edit_bw':
        img = img.convert('L')
        caption = "Lo bhai, Black & White filter laga diya! ⚫"
    elif query.data == 'edit_blur':
        img = img.filter(ImageFilter.GaussianBlur(radius=5))
        caption = "Photo blur kar di gayi hai! 🌫️"
    elif query.data == 'edit_resize':
        img.thumbnail((300, 300))
        caption = "Photo ko resize (thumbnail) kar diya gaya hai! 📐"

    img.save(output_path)
    
    with open(output_path, 'rb') as edited_photo:
        await query.message.reply_photo(photo=edited_photo, caption=caption)

    if os.path.exists(file_path):
        os.remove(file_path)
    if os.path.exists(output_path):
        os.remove(output_path)
    context.user_data.pop('photo_path', None)
