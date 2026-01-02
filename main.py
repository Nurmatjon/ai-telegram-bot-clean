import os
import json
import logging
import asyncio
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    Application,
)

from scheduler import (
    scheduler_loop,
    send_post,
    load_state,
    save_state,
)

# ================= LOGGING =================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# ================= ENV =================
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
SCHEDULE_FILE = "data/schedule.json"

if not BOT_TOKEN:
    raise RuntimeError("❌ BOT_TOKEN topilmadi")

# ================= ADMIN KEYBOARD =================
def admin_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("💰 Pul posti", callback_data="post_money"),
            InlineKeyboardButton("🧠 Kasb posti", callback_data="post_skill"),
        ],
        [
            InlineKeyboardButton("🔥 Motivatsiya", callback_data="post_motivation"),
        ],
        [
            InlineKeyboardButton("⏸ To‘xtatish", callback_data="pause"),
            InlineKeyboardButton("▶️ Yoqish", callback_data="resume"),
        ],
        [
            InlineKeyboardButton("⏰ Vaqtni o‘zgartirish", callback_data="set_time"),
            InlineKeyboardButton("📊 Holat", callback_data="status"),
        ]
    ])

# ================= COMMANDS =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Bot ishlayapti (custom scheduler).")

async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    await update.message.reply_text("🎛 Admin panel:", reply_markup=admin_keyboard())

# ================= CALLBACK =================
async def admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.from_user.id != ADMIN_ID:
        return

    data = query.data
    state = load_state()

    if data.startswith("post_"):
        post_type = data.replace("post_", "")
        await send_post(context.bot, post_type)

    elif data == "pause":
        state["enabled"] = False
        save_state(state)
        await query.message.reply_text("⏸ Avto postlar o‘chirildi")

    elif data == "resume":
        state["enabled"] = True
        save_state(state)
        await query.message.reply_text("▶️ Avto postlar yoqildi")

    elif data == "status":
        status = "YOQILGAN ✅" if state.get("enabled", True) else "O‘CHIQ ⛔"
        await query.message.reply_text(f"📊 Holat: {status}")

    elif data == "set_time":
        await query.message.reply_text(
            "⏰ Vaqtni o‘zgartirish:\n\n"
            "/set_time money 09:00\n"
            "/set_time skill 16:00\n"
            "/set_time motivation 21:00\n\n"
            "♻️ Darhol kuchga kiradi"
        )

# ================= SET TIME =================
async def set_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    try:
        post_type = context.args[0]
        new_time = context.args[1]
        h, m = map(int, new_time.split(":"))
        if post_type not in ("money", "skill", "motivation"):
            raise ValueError
    except:
        await update.message.reply_text("❌ Format: /set_time skill 16:30")
        return

    data = {}
    if os.path.exists(SCHEDULE_FILE):
        with open(SCHEDULE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

    data[post_type] = new_time
    os.makedirs("data", exist_ok=True)

    with open(SCHEDULE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    await update.message.reply_text(
        f"✅ `{post_type}` posti vaqti `{new_time}` ga o‘zgartirildi",
        parse_mode="Markdown"
    )

# ================= POST INIT (ENG MUHIM) =================
async def post_init(application: Application):
    logger.info("⏰ Custom scheduler ishga tushyapti")
    application.create_task(scheduler_loop(application.bot))

# ================= MAIN =================
def main():
    app = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .post_init(post_init)  # 🔥 MUHIM JOY
        .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin))
    app.add_handler(CommandHandler("set_time", set_time))
    app.add_handler(CallbackQueryHandler(admin_callback))

    app.run_polling(drop_pending_updates=True)

# ================= ENTRY =================
if __name__ == "__main__":
    main()
