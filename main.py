import os
import logging
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
)

from scheduler import setup_scheduler, post_job, load_state, save_state

# ================= LOGGING =================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# ================= ENV =================
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

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
            InlineKeyboardButton("📊 Holat", callback_data="status"),
        ]
    ])

# ================= COMMANDS =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Bot ishlayapti.")

async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    await update.message.reply_text(
        "🎛 Admin panel:",
        reply_markup=admin_keyboard()
    )

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
        await query.message.reply_text(f"📤 {post_type} posti yuborilmoqda...")
        context.job.data = post_type
        await post_job(context)

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
        await query.message.reply_text(f"📊 Avto post holati: {status}")

# ================= MAIN =================
def main():
    logger.info("🚀 Bot ishga tushyapti")

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin))
    app.add_handler(CallbackQueryHandler(admin_callback))

    setup_scheduler(app)
    logger.info("⏰ Scheduler ishga tushdi")

    app.run_polling(drop_pending_updates=True)

# ================= ENTRY =================
if __name__ == "__main__":
    main()
