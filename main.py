# -*- coding: utf-8 -*-
"""
Created on Thu Jan  1 14:29:12 2026

@author: User
"""

import asyncio
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from bot import router
from scheduler import setup_scheduler

async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)

    setup_scheduler(bot)

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
