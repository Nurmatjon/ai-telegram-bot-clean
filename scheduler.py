from zoneinfo import ZoneInfo
import json
import os
import asyncio
import logging
from datetime import datetime

from ai_engine import generate_post
from content_logic import get_topic
from config import CHANNEL_ID as _CHANNEL_ID

CHANNEL_ID = int(_CHANNEL_ID)
logger = logging.getLogger(__name__)

STATE_FILE = "data/state.json"
SCHEDULE_FILE = "data/schedule.json"

DEFAULT_SCHEDULE = {
    "money": "08:00",
    "skill": "15:00",
    "motivation": "20:00",
}

# ================= STATE =================
def load_state():
    if not os.path.exists(STATE_FILE):
        return {"day": 0, "enabled": True, "last_sent": {}}
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_state(state):
    os.makedirs("data", exist_ok=True)
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

# ================= SCHEDULE =================
def load_schedule():
    if not os.path.exists(SCHEDULE_FILE):
        return DEFAULT_SCHEDULE
    with open(SCHEDULE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

# ================= FORMAT =================
def format_post_text(text: str) -> str:
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    if not lines:
        return text

    out = [f"*{lines[0]}*", ""]

    for line in lines[1:]:
        if line.startswith("####"):
            title = line.replace("####", "").strip()
            out.append(f"! *{title}*")
            out.append("")
        else:
            out.append(line)
            out.append("")

    return "\n".join(out).strip()

# ================= POST =================
async def send_post(bot, post_type: str):
    state = load_state()
    if not state.get("enabled", True):
        return

    index = state.get("day", 0)
    topic = get_topic(index)

    raw = generate_post(topic, post_type=post_type)
    post = format_post_text(raw)

    await bot.send_message(
        chat_id=CHANNEL_ID,
        text=post,
        parse_mode="Markdown"
    )

    state["day"] = index + 1
    state.setdefault("last_sent", {})[post_type] = datetime.now().strftime("%Y-%m-%d")
    save_state(state)

    logger.info(f"✅ {post_type} posti yuborildi")

# ================= MAIN LOOP =================
async def scheduler_loop(bot):
    logger.info("🟢 SCHEDULER LOOP STARTED")

    # 🔥 ISBOT UCHUN — ISHGA TUSHGANDA XABAR
    try:
        await bot.send_message(
            chat_id=CHANNEL_ID,
            text="🧪 Scheduler ishga tushdi (TEST XABAR)"
        )
    except Exception as e:
        logger.error(f"Scheduler test xabar xatosi: {e}")

    while True:
        try:
            logger.info("⏳ Scheduler tirik (30s tekshiruv)")

            tz = ZoneInfo("Asia/Tashkent")
            now_dt = datetime.now(tz)
            now = now_dt.strftime("%H:%M")
            today = now_dt.strftime("%Y-%m-%d")


            schedule = load_schedule()
            state = load_state()
            last_sent = state.get("last_sent", {})

            for post_type, post_time in schedule.items():
                if now == post_time and last_sent.get(post_type) != today:
                    await send_post(bot, post_type)

        except Exception as e:
            logger.error(f"SCHEDULER ERROR: {e}")

        await asyncio.sleep(30)
