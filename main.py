import os
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

from scheduler import setup_scheduler   # ⏰ sizdagi scheduler.py

# =====================================================
# LOGGING (Railway loglari uchun muhim)
# =====================================================
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# =====================================================
# BOT TOKEN (ENV)
# =====================================================
BOT_TOKEN = os.environ["BOT_TOKEN"]  # ❗ qat’iy (production uchun to‘g‘ri)

# =====================================================
# /start komandasi
# =====================================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Salom! Bot ishlayapti.")

# =====================================================
# MAIN
# =====================================================
def main():
    logger.info("🚀 Bot ishga tushyapti")

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # /start handler
    app.add_handler(CommandHandler("start", start))

    # ⏰ SCHEDULERNI ISHGA TUSHIRISH (ENG MUHIM JOY)
    setup_scheduler(app.bot)
    logger.info("⏰ Scheduler ulandi (har kuni 11:35)")

    # 🔁 Polling (Railway uchun to‘g‘ri)
    logger.info("🔁 Polling boshlandi")
    app.run_polling(drop_pending_updates=True)

# =====================================================
if __name__ == "__main__":
    main()
