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
SCHEDULE_FILE = "data/schedule.json"

# ================= STATE =================
def load_state():
    if not os.path.exists(STATE_FILE):
        return {"day": 0, "enabled": True}
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_state(state):
    os.makedirs("data", exist_ok=True)
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

# ================= SCHEDULE =================
def load_schedule():
    """
    schedule.json dan vaqtlarni o‘qiydi.
    Agar fayl yo‘q bo‘lsa — default vaqtlar.
    """
    if not os.path.exists(SCHEDULE_FILE):
        return {
            "money": time(8, 0),
            "skill": time(15, 0),
            "motivation": time(20, 0),
        }

    with open(SCHEDULE_FILE, "r", encoding="utf-8") as f:
        raw = json.load(f)

    result = {}
    for key, value in raw.items():
        h, m = map(int, value.split(":"))
        result[key] = time(hour=h, minute=m)

    return result

# ================= FORMAT =================
def format_post_text(text: str) -> str:
    """
    - Asosiy sarlavha qalin
    - #### -> !
    - ! dan keyingi sarlavha qalin
    - Har abzatsdan keyin 1 bo‘sh qator
    """
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    if not lines:
        return text

    formatted = []
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

    state = load_state()
    if not state.get("enabled", True):
        logger.info("⏸ Avto postlar o‘chiq")
        return

    logger.info(f"🕘 Post turi: {post_type}")

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

    logger.info("✅ Post yuborildi")

# ================= JOB QUEUE =================
def setup_scheduler(application):
    jq = application.job_queue

    # ❌ ESKI JOBLARNI TO‘LIQ O‘CHIRISH
    for job in jq.jobs():
        job.schedule_removal()

    # ✅ YANGI VAQTLARNI O‘QISH
    schedule = load_schedule()

    jq.run_daily(
        post_job,
        time=schedule["money"],
        data="money",
        name="post_money"
    )

    jq.run_daily(
        post_job,
        time=schedule["skill"],
        data="skill",
        name="post_skill"
    )

    jq.run_daily(
        post_job,
        time=schedule["motivation"],
        data="motivation",
        name="post_motivation"
    )

    logger.info(
        "⏰ Scheduler yangilandi: "
        f"money={schedule['money']}, "
        f"skill={schedule['skill']}, "
        f"motivation={schedule['motivation']}"
    )
