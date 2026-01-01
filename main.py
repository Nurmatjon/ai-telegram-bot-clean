import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ===== LOGGING (Railway logs ko‘rinishi uchun) =====
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ===== BOT TOKEN =====
BOT_TOKEN = os.environ.get("BOT_TOKEN")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN environment variable topilmadi")

# ===== /start komandasi =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("/start komandasi keldi")
    await update.message.reply_text("Salom! Bot ishlayapti ✅")

# ===== MAIN =====
def main():
    logger.info("Bot ishga tushyapti...")

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    logger.info("Polling boshlandi")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
