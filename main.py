import os
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

# LOGGING (Railway loglari uchun juda muhim)
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN topilmadi")

# /start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Salom! Bot ishlayapti.")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # /start handler
    app.add_handler(CommandHandler("start", start))

    print("BOT ALIVE")

    # polling (Railway uchun to‘g‘ri)
    app.run_polling()

if __name__ == "__main__":
    main()
