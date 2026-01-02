import os
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

from scheduler import setup_scheduler, post_job

# ================= LOGGING =================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

print("🔥 main.py LOADED")

# ================= ENV =================
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

if not BOT_TOKEN:
    raise RuntimeError("❌ BOT_TOKEN topilmadi (Railway Variables tekshiring)")

# ================= COMMANDS =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Bot ishlayapti. Avtomatik postlar yoqilgan.")

async def test_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    await update.message.reply_text("🧪 Test post yuborilmoqda...")
    await post_job(context)
    await update.message.reply_text("✅ Test post tugadi")

# ================= MAIN =================
def main():
    logger.info("🚀 Bot ishga tushyapti")

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("test_post", test_post))

    # ⏰ Scheduler
    setup_scheduler(app)
    logger.info("⏰ Scheduler ulandi")

    logger.info("🔁 Polling boshlandi")
    app.run_polling(drop_pending_updates=True)

# ================= ENTRY =================
if __name__ == "__main__":
    main()
