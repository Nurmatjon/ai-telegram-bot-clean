import os
import logging
from telegram.ext import ApplicationBuilder, CommandHandler
from scheduler import post_job
from datetime import time

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.environ["BOT_TOKEN"]

async def start(update, context):
    await update.message.reply_text("👋 Bot ishlayapti.")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    # ✅ TO‘G‘RI CRON — PTB JobQueue
    app.job_queue.run_daily(
        post_job,
        time=time(hour=12, minute=17),          # ⏰ 12:17
        days=(0,1,2,3,4,5,6),
        name="daily_post"
    )

    logging.info("🚀 Bot started with PTB JobQueue (12:17)")

    app.run_polling()

if __name__ == "__main__":
    main()
