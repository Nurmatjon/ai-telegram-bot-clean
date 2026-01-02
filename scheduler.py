import json
import os
import logging
from datetime import time

from telegram.ext import ContextTypes
from aiogram.types import FSInputFile  # sizda rasm shu orqali ketayapti

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
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

# =====================================================
# FORMAT HELPERS
# =====================================================
def bold_title(post_text: str) -> str:
    lines = [l.strip() for l in post_text.split("\n") if l.strip()]
    if not lines:
        return post_text
    return f"**{lines[0]}**\n\n" + "\n".join(lines[1:])

def make_short_caption(text: str, limit: int = 900) -> str:
    if len(text) <= limit:
        return text
    return text[:limit].rsplit(" ", 1)[0] + "…\n\n⬇️ Davomi pastda"

def detect_theme(topic: str) -> str:
    t = topic.lower()
    if "kasb" in t or "o‘rgan" in t:
        return "kasb"
    if "motiv" in t or "sabr" in t:
        return "motivatsiya"
    return "pul"

# =====================================================
# ASOSIY POST ISHI
# =====================================================
async def post_job(context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    logger.info("🕘 Scheduled post boshlandi")

    state = load_state()
    day_index = state.get("day", 0)

    topic = get_topic(day_index)
    full_post = bold_title(generate_post(topic))

    image_text = fit_text_for_image(generate_image_text(full_post))
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

    # 1-rasm + caption
    await bot.send_photo(
        chat_id=CHANNEL_ID,
        photo=FSInputFile(image_paths[0]),
        caption=short_caption,
        parse_mode="Markdown"
    )

    # To‘liq post
    await bot.send_message(
        chat_id=CHANNEL_ID,
        text=full_post,
        parse_mode="Markdown"
    )

    # Qolgan rasmlar
    for path in image_paths[1:]:
        await bot.send_photo(
            chat_id=CHANNEL_ID,
            photo=FSInputFile(path)
        )

    # Cleanup
    for path in image_paths:
        if os.path.exists(path):
            os.remove(path)

    state["day"] = day_index + 1
    save_state(state)

    logger.info("✅ Scheduled post yuborildi")

# =====================================================
# JOBQUEUE SETUP
# =====================================================
def setup_scheduler(application):
    job_queue = application.job_queue

    # 🔔 HAR KUNI 11:40 (Asia/Tashkent)
    job_queue.run_daily(
        post_job,
        time=time(hour=12, minute=45),
        name="daily_post",
        days=(0, 1, 2, 3, 4, 5, 6),
    )

    logger.info("⏰ JobQueue scheduler ulandi (har kuni 12:45)")
