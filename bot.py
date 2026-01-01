# -*- coding: utf-8 -*-
"""
Admin boshqaruv moduli
"""

from aiogram import Router, types
from aiogram.filters import Command
from config import ADMIN_ID
from scheduler import post_job
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

router = Router()

# =====================================================
# /status — bot holatini tekshirish
# =====================================================
@router.message(Command("status"))
async def status(msg: types.Message):
    if msg.from_user.id == ADMIN_ID:
        await msg.answer("✅ Bot ishlayapti")
    else:
        await msg.answer("❌ Siz admin emassiz")

# =====================================================
# /admin — admin panel
# =====================================================
@router.message(Command("admin"))
async def admin_panel(msg: types.Message):
    if msg.from_user.id != ADMIN_ID:
        await msg.answer("❌ Siz admin emassiz")
        return

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🚀 Hozir post chiqar",
                    callback_data="post_now"
                )
            ]
        ]
    )

    await msg.answer("🎛 Admin panel:", reply_markup=keyboard)

# =====================================================
# Callback — Hozir post chiqarish
# =====================================================
@router.callback_query(lambda c: c.data == "post_now")
async def post_now_callback(call: types.CallbackQuery, bot):
    if call.from_user.id != ADMIN_ID:
        await call.answer("Ruxsat yo‘q", show_alert=True)
        return

    await call.answer("Post chiqarilmoqda...")
    await post_job(bot)
    await call.message.answer("✅ Post muvaffaqiyatli chiqarildi")
