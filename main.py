import os
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

from scheduler import setup_scheduler, post_job

# =====================================================
# LOGGING — Railway uchun MAJBURIY
# =====================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

print("🔥 main.py LOADED")

# =====================================================
# BOT TOKEN
# =====================================================
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise RuntimeError("❌ BOT_TOKEN topilmadi (Railway Variables tekshiring)")

# =====================================================
# /start
# =====================================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("/start bosildi")
    await update.message.reply_text("👋 Bot ishlayapti (DEBUG MODE)")

# =====================================================
# /test_post — qo‘lda post chiqarish (ENG MUHIM)
# =====================================================
async def test_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("🧪 TEST POST qo‘lda ishga tushdi")
    await update.message.reply_text("🧪 Test post yuborilmoqda...")
    await post_job(context.bot)
    await update.message.reply_text("✅ Test post tugadi")

# =====================================================
# MAIN
# =====================================================
def main():
    logger.info("🚀 BOT ISHGA TUSHYAPTI")

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("test_post", test_post))

    # ⏰ Scheduler
    setup_scheduler(app.bot)
    logger.info("⏰ Scheduler ulandi")

    logger.info("🔁 Polling boshlandi")
    app.run_polling(drop_pending_updates=True)

# =====================================================
if __name__ == "__main__":
    main()
