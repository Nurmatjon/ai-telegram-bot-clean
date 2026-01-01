# -*- coding: utf-8 -*-
"""
Created on Thu Jan  1 16:09:51 2026

@author: User
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

admin_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🚀 Hozir post chiqar", callback_data="post_now")]
    ]
)
