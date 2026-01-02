import os
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

from scheduler import setup_scheduler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN topilmadi")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Bot ishlayapti")

# ✅ TO‘G‘RI TEST POST
async def test_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🧪 Test post 10 soniyada yuboriladi")
    context.job_queue.run_once(
        callback=context.application.job_queue.jobs()[0].callback
        if context.application.job_queue.jobs()
        else None,
        when=10
    )

def main():
    logger.info("🚀 Bot ishga tushdi")

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("test_post", test_post))

    setup_scheduler(app)

    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
