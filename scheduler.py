import json
import os
import logging
from datetime import time

from telegram import InputFile
from telegram.ext import ContextTypes

from ai_engine import generate_post, generate_image_text, fit_text_for_image
from content_logic import get_topic
from image_engine import generate_image_block
from carousel_engine import build_carousel
from config import CHANNEL_ID

logger = logging.getLogger(__name__)

STATE_FILE = "data/state.json"

# ================= STATE =================
def load_state():
    if not os.path.exists(STATE_FILE):
        return {"day": 0}
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_state(state):
    os.makedirs("data", exist_ok=True)
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

# ================= FORMAT =================
def bold_title(text: str) -> str:
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    if not lines:
        return text
    return f"**{lines[0]}**\n\n" + "\n".join(lines[1:])

def make_short_caption(text: str, limit=900):
    if len(text) <= limit:
        return text
    return text[:limit].rsplit(" ", 1)[0] + "…\n\n⬇️ Davomi pastda"

def detect_theme(topic: str):
    t = topic.lower()
    if "kasb" in t:
        return "kasb"
    if "motiv" in t:
        return "motivatsiya"
    return "pul"

# ================= POST JOB =================
async def post_job(context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    logger.info("🕘 Scheduled post boshlandi")

    state = load_state()
    day = state.get("day", 0)

    topic = get_topic(day)
    full_post = bold_title(generate_post(topic))

    image_text = fit_text_for_image(generate_image_text(full_post))
    theme = detect_theme(topic)

    blocks = build_carousel(image_text)
    image_paths = []

    for i, block in enumerate(blocks):
        path = generate_image_block(
            data=block,
            theme=theme,
            filename=f"data/post_{day}_{i}.png"
        )
        image_paths.append(path)

    short_caption = make_short_caption(full_post)

    # 1-rasm
    await bot.send_photo(
        chat_id=CHANNEL_ID,
        photo=InputFile(image_paths[0]),
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
            photo=InputFile(path)
        )

    for path in image_paths:
        if os.path.exists(path):
            os.remove(path)

    state["day"] = day + 1
    save_state(state)

    logger.info("✅ Scheduled post yuborildi")

# ================= JOB QUEUE =================
def setup_scheduler(application):
    jq = application.job_queue

    jq.run_daily(
        post_job,
        time=time(hour=13, minute=10),  # ⏰ shu yerda vaqt
        name="daily_post"
    )

    logger.info("⏰  JobQueue scheduler ulandi")
