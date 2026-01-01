# -*- coding: utf-8 -*-
"""
Created on Thu Jan  1 13:41:27 2026

@author: User
"""

import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

ADMIN_ID = 851981172  # o‘zingizning Telegram ID
CHANNEL_ID = -1003179094502  # kanal ID
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

POST_TIME_MORNING = "09:00"
POST_TIME_EVENING = "19:00"
