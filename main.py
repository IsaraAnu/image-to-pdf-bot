import os
import logging
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from PIL import Image
from io import BytesIO

BOT_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    logging.info(f"User {user.id} sent an image.")
    photo_file = await update.message.photo[-1].get_file()
    photo_bytes = await photo_file.download_as_bytearray()

    if 'images' not in context.user_data:
        context.user_data['images'] = []
    context.user_data['images'].append(BytesIO(photo_bytes))

    await update.message.reply_text("Image received! Send more or type /pdf.")

async def generate_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'images' not in context.user_data or len(context.user_data['images']) == 0:
        await update.message.reply_text("No images found!")
        return

    images = [Image.open(img) for img in context.user_data['images']]
    pdf_bytes = BytesIO()
    images[0].save(pdf_bytes, save_all=True, append_images=images[1:], format="PDF")
    pdf_bytes.seek(0)

    await update.message.reply_document(document=pdf_bytes, filename="output.pdf")
    context.user_data['images'] = []

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.PHOTO, handle_image))
    app.add_handler(MessageHandler(filters.Regex(r'/pdf'), generate_pdf))
    app.run_polling()

if __name__ == "__main__":
    main()
