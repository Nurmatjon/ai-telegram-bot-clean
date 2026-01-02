from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import logging
import json
import os

from telegram import Bot, InputFile
from config import CHANNEL_ID

from ai_engine import generate_post, generate_image_text, fit_text_for_image
from content_logic import get_topic
from image_engine import generate_image_block
from carousel_engine import build_carousel

logger = logging.getLogger(__name__)

STATE_FILE = "data/state.json"

def load_state():
    if not os.path.exists(STATE_FILE):
        return {"day": 0}
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def bold_title(text: str) -> str:
    lines = [l for l in text.split("\n") if l.strip()]
    if not lines:
        return text
    return f"*{lines[0]}*\n\n" + "\n".join(lines[1:])

async def post_job(bot: Bot):
    logger.info("⏰ POST JOB STARTED")

    state = load_state()
    day = state["day"]

    topic = get_topic(day)
    full_post = bold_title(generate_post(topic))

    image_text = fit_text_for_image(generate_image_text(full_post))
    blocks = build_carousel(image_text)

    image_paths = []
    for i, block in enumerate(blocks):
        path = generate_image_block(
            data=block,
            theme="pul",
            filename=f"data/post_{day}_{i}.png"
        )
        image_paths.append(path)

    await bot.send_photo(
        chat_id=CHANNEL_ID,
        photo=InputFile(image_paths[0]),
        caption=full_post[:900],
        parse_mode="Markdown"
    )

    await bot.send_message(
        chat_id=CHANNEL_ID,
        text=full_post,
        parse_mode="Markdown"
    )

    for p in image_paths:
        if os.path.exists(p):
            os.remove(p)

    state["day"] = day + 1
    save_state(state)

    logger.info("✅ POST SENT SUCCESSFULLY")

def setup_scheduler(bot: Bot):
    scheduler = AsyncIOScheduler(timezone="Asia/Tashkent")

    scheduler.add_job(
        post_job,
        CronTrigger(hour=11, minute=40),
        args=[bot],
        id="daily_post",
        replace_existing=True
    )

    scheduler.start()
    logger.info("🚀 Scheduler started (11:40)")
