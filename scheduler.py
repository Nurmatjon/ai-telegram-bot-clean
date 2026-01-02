import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot
from aiogram.types import FSInputFile
import os
import json

from ai_engine import generate_post, generate_image_text, fit_text_for_image
from content_logic import get_topic
from image_engine import generate_image_block
from carousel_engine import build_carousel
from config import CHANNEL_ID

logger = logging.getLogger(__name__)

STATE_FILE = "data/state.json"

# =====================================================
def load_state():
    if not os.path.exists(STATE_FILE):
        logger.info("📁 state.json yo‘q — 0 dan boshlanadi")
        return {"day": 0}
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_state(state):
    os.makedirs("data", exist_ok=True)
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

# =====================================================
async def post_job(bot: Bot):
    try:
        logger.info("🟢 post_job ISHGA TUSHDI")

        state = load_state()
        day_index = state.get("day", 0)
        logger.info(f"📆 Day index: {day_index}")

        topic = get_topic(day_index)
        logger.info(f"📝 Topic: {topic}")

        full_post = generate_post(topic)
        image_text = generate_image_text(full_post)
        image_text = fit_text_for_image(image_text)

        blocks = build_carousel(image_text)
        image_paths = []

        for i, block in enumerate(blocks):
            path = generate_image_block(
                data=block,
                theme="default",
                filename=f"data/post_{day_index}_{i}.png"
            )
            image_paths.append(path)

        logger.info("📤 Telegramga yuborilmoqda")

        await bot.send_photo(
            chat_id=CHANNEL_ID,
            photo=FSInputFile(image_paths[0]),
            caption=full_post[:900],
            parse_mode="Markdown"
        )

        await bot.send_message(
            chat_id=CHANNEL_ID,
            text=full_post,
            parse_mode="Markdown"
        )

        for path in image_paths:
            if os.path.exists(path):
                os.remove(path)

        state["day"] = day_index + 1
        save_state(state)

        logger.info("✅ POST MUVAFFAQIYATLI YUBORILDI")

    except Exception as e:
        logger.exception("❌ post_job XATOLIK BILAN TO‘XTADI")

# =====================================================
def setup_scheduler(bot: Bot):
    logger.info("⏰ Scheduler yaratilyapti")

    scheduler = AsyncIOScheduler(timezone="Asia/Tashkent")

    scheduler.add_job(
        post_job,
        trigger="cron",
        hour=12,
        minute=35,
        args=[bot],
        id="daily_post"
    )

    scheduler.start()
    logger.info("⏰ Scheduler START qilindi (11:40)")
