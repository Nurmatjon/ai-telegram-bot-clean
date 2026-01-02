from apscheduler.schedulers.asyncio import AsyncIOScheduler
from ai_engine import (
    generate_post,
    generate_image_text,
    fit_text_for_image
)
from content_logic import get_topic
from image_engine import generate_image_block
from carousel_engine import build_carousel
from config import CHANNEL_ID
from aiogram import Bot
from aiogram.types import FSInputFile
import json
import os

STATE_FILE = "data/state.json"

# =====================================================
# STATE (kunlarni saqlash)
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
# POST SARLAVHASINI QALIN QILISH
# =====================================================
def bold_title(post_text: str) -> str:
    lines = [l.strip() for l in post_text.split("\n") if l.strip()]
    if not lines:
        return post_text

    title = lines[0]
    body = "\n".join(lines[1:])
    return f"**{title}**\n\n{body}"

# =====================================================
# CAPTIONNI QISQARTIRISH (Telegram limit)
# =====================================================
def make_short_caption(post_text: str, limit: int = 900) -> str:
    if len(post_text) <= limit:
        return post_text

    short = post_text[:limit]
    short = short.rsplit(" ", 1)[0]
    return short + "…\n\n⬇️ Davomi pastda"

# =====================================================
# MAVZU ANIQLASH
# =====================================================
def detect_theme(topic: str) -> str:
    t = topic.lower()
    if "kasb" in t or "o‘rgan" in t:
        return "kasb"
    if "motiv" in t or "sabr" in t or "harakat" in t:
        return "motivatsiya"
    return "pul"

# =====================================================
# ASOSIY POST ISHI (KUNIGA 1 MARTA)
# =====================================================
async def post_job(bot: Bot):
    state = load_state()
    day_index = state.get("day", 0)

    # 1️⃣ Mavzu
    topic = get_topic(day_index)

    # 2️⃣ To‘liq post
    full_post = generate_post(topic)
    full_post = bold_title(full_post)

    # 3️⃣ Rasm uchun qisqa matn
    image_text = generate_image_text(full_post)
    image_text = fit_text_for_image(image_text)

    # 4️⃣ Rang mavzusi
    theme = detect_theme(topic)

    # 5️⃣ Carousel bloklari
    carousel_blocks = build_carousel(image_text)
    image_paths = []

    # 6️⃣ Rasmlarni yaratish
    for i, block in enumerate(carousel_blocks):
        path = generate_image_block(
            data=block,
            theme=theme,
            filename=f"data/post_{day_index}_{i}.png"
        )
        image_paths.append(path)

    # 7️⃣ Telegramga yuborish
    short_caption = make_short_caption(full_post)

    # 1-rasm: qisqa caption
    await bot.send_photo(
        chat_id=CHANNEL_ID,
        photo=FSInputFile(image_paths[0]),
        caption=short_caption,
        parse_mode="Markdown"
    )

    # To‘liq post: alohida xabar
    await bot.send_message(
        chat_id=CHANNEL_ID,
        text=full_post,
        parse_mode="Markdown"
    )

    # Qolgan rasmlar (agar bo‘lsa)
    for path in image_paths[1:]:
        await bot.send_photo(
            chat_id=CHANNEL_ID,
            photo=FSInputFile(path)
        )

    # 8️⃣ Rasmlarni tozalash
    for path in image_paths:
        if os.path.exists(path):
            os.remove(path)

    # 9️⃣ STATE yangilash
    state["day"] = day_index + 1
    save_state(state)

# =====================================================
# SCHEDULER — KUNIGA BITTA POST
# =====================================================
def setup_scheduler(bot: Bot):
    scheduler = AsyncIOScheduler(timezone="Asia/Tashkent")

    # ✅ HAR KUNI SOAT 11:00 DA
    scheduler.add_job(
        post_job,
        trigger="cron",
        hour=11,
        minute=0,
        args=[bot]
    )

    scheduler.start()
