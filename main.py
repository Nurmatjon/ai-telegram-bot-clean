import os
import asyncio
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from openai import OpenAI


# =====================
# ENVIRONMENT VARIABLES
# =====================
BOT_TOKEN = os.ENVIRON["BOT_TOKEN"]
OPENAI_API_KEY = os.ENVIRON["OPENAI_API_KEY"]

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN topilmadi (Railway Variables)")

if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY topilmadi (Railway Variables)")


# =====================
# LOGGING
# =====================
logging.basicConfig(level=logging.INFO)


# =====================
# OPENAI CLIENT
# =====================
client = OpenAI(
    api_key=OPENAI_API_KEY
)


# =====================
# TELEGRAM BOT
# =====================
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


# =====================
# HANDLERS
# =====================
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer("Salom! AI bot ishga tushdi ✅")


@dp.message()
async def ai_handler(message: types.Message):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": message.text}
            ]
        )

        answer = response.choices[0].message.content
        await message.answer(answer)

    except Exception as e:
        logging.exception("OpenAI xatosi")
        await message.answer("❌ Xatolik yuz berdi, keyinroq urinib ko‘ring.")


# =====================
# MAIN
# =====================
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
