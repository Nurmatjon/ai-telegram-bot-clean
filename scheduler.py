from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import logging
import json
import os

from aiogram import Bot
from aiogram.types import FSInputFile

from ai_engine import (
    generate_post,
    generate_image_text,
    fit_text_for_image
)
from content_logic import get_topic
from image_engine import generate_image_block
from carousel_engine import build_carousel
from config import CHANNEL_ID

logger = logging.getLogger(__name__)

STATE_FILE = "data/state.json"

# =====================================================
# STATE
# =====================================================
def load_state():
    if not os.path.exists(STATE_FILE):
        return {"day": 0}
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

# =====================================================
# YORDAMCHI FUNKSIYALAR
# =====================================================
def bold_title(post_text: str) -> str:
    lines = [l.strip() for l in post_text.split("\n") if l.strip()]
    if not lines:
        return post_text
    title = lines[0]
    body = "\n".join(lines[1:])
    return f"**{title}**\n\n{body}"

def make_short_caption(post_text: str, limit: int = 900) -> str:
    if len(post_text) <= limit:
        return post_text
    short = post_text[:limit].rsplit(" ", 1)[0]
    return short + "…\n\n⬇️ Davomi pastda"

def detect_theme(topic: str) -> str:
    t = topic.lower()
    if "kasb" in t or "o‘rgan" in t:
        return "kasb"
    if "motiv" in t or "sabr" in t or "harakat" in t:
        return "motivatsiya"
    return "pul"

# =====================================================
# ASOSIY POST JOB
# =====================================================
async def post_job(bot: Bot):
    logger.info("⏰ Scheduler job started")

    state = load_state()
    day_index = state.get("day", 0)

    topic = get_topic(day_index)
    full_post = bold_title(generate_post(topic))

    image_text = fit_text_for_image(
        generate_image_text(full_post)
    )

    theme = detect_theme(topic)
    carousel_blocks = build_carousel(image_text)
    image_paths = []

    for i, block in enumerate(carousel_blocks):
        path = generate_image_block(
            data=block,
            theme=theme,
            filename=f"data/post_{day_index}_{i}.png"
        )
        image_paths.append(path)

    short_caption = make_short_caption(full_post)

    await bot.send_photo(
        chat_id=CHANNEL_ID,
        photo=FSInputFile(image_paths[0]),
        caption=short_caption,
        parse_mode="Markdown"
    )

    await bot.send_message(
        chat_id=CHANNEL_ID,
        text=full_post,
        parse_mode="Markdown"
    )

    for path in image_paths[1:]:
        await bot.send_photo(chat_id=CHANNEL_ID, photo=FSInputFile(path))

    for path in image_paths:
        if os.path.exists(path):
            os.remove(path)

    state["day"] = day_index + 1
    save_state(state)

    logger.info("✅ Scheduler job finished")

# =====================================================
# SCHEDULER SETUP (ENG MUHIM JOY)
# =====================================================
def setup_scheduler(bot: Bot):
    scheduler = AsyncIOScheduler(timezone="Asia/Tashkent")

    scheduler.add_job(
        post_job,
        trigger=CronTrigger(hour=11, minute=20),
        args=[bot],
        id="daily_post",              # MUHIM
        replace_existing=True,        # MUHIM
        max_instances=1               # MUHIM
    )

    scheduler.start()
    logger.info("🚀 Scheduler started: every day at 11:20 Asia/Tashkent")
