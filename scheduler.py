import json
import os
import logging
from datetime import time
from telegram.ext import ContextTypes

from ai_engine import generate_post
from content_logic import get_topic
from config import CHANNEL_ID as _CHANNEL_ID

CHANNEL_ID = int(_CHANNEL_ID)
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
def format_post_text(text: str) -> str:
    """
    Qoidalar:
    - Asosiy sarlavha qalin
    - #### -> !
    - ! dan keyingi sarlavha qalin
    - Har abzatsdan keyin 1 bo‘sh qator
    """
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    if not lines:
        return text

    formatted = []

    # Asosiy sarlavha
    formatted.append(f"*{lines[0]}*")
    formatted.append("")

    for line in lines[1:]:
        if line.startswith("####"):
            title = line.replace("####", "").strip()
            formatted.append(f"! *{title}*")
            formatted.append("")
        else:
            formatted.append(line)
            formatted.append("")

    return "\n".join(formatted).strip()

def limit_text(text: str, limit: int = 3500) -> str:
    if len(text) <= limit:
        return text
    return text[:limit].rsplit(" ", 1)[0] + "…"

# ================= POST JOB =================
async def post_job(context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    post_type = context.job.data  # money / skill / motivation

    logger.info(f"🕘 Post turi: {post_type}")

    state = load_state()
    index = state.get("day", 0)

    topic = get_topic(index)
    raw_post = generate_post(topic, post_type=post_type)

    post = format_post_text(raw_post)
    post = limit_text(post)

    await bot.send_message(
        chat_id=CHANNEL_ID,
        text=post,
        parse_mode="Markdown"
    )

    state["day"] = index + 1
    save_state(state)

    logger.info("✅ Matnli post yuborildi")

# ================= JOB QUEUE =================
def setup_scheduler(application):
    jq = application.job_queue

    jq.run_daily(
        post_job,
        time=time(hour=8, minute=0),
        data="money",
        name="post_08"
    )

    jq.run_daily(
        post_job,
        time=time(hour=15, minute=0),
        data="skill",
        name="post_15"
    )

    jq.run_daily(
        post_job,
        time=time(hour=20, minute=0),
        data="motivation",
        name="post_20"
    )

    logger.info("⏰ JobQueue scheduler ulandi (08:00 / 15:00 / 20:00)")
