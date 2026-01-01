# -*- coding: utf-8 -*-
"""
Created on Thu Jan  1 14:21:46 2026

@author: User
"""

TOPICS = [
    "Pul topish nima va nega muhim",
    "Pul topish yo‘llari turlari",
    "Kasb nima va daromad bilan bog‘liqligi",
    "Talab yuqori kasblar",
    "Bilimni pulga aylantirish",
    "Motivatsiya: sabr va intizom",
    "Xatolar va noto‘g‘ri yo‘llar"
]

def get_topic(day_index: int) -> str:
    return TOPICS[day_index % len(TOPICS)]
