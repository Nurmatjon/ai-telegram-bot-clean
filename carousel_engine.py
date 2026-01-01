# -*- coding: utf-8 -*-
"""
Created on Thu Jan  1 15:38:16 2026

@author: User
"""

def build_carousel(image_text: dict):
    """
    3 rasmli carousel uchun bo‘lish
    """
    return [
        {
            "title": image_text["title"],
            "body": "",
            "question": "Bu muammo sizda ham bormi?"
        },
        {
            "title": "Yechim nimada?",
            "body": image_text["body"],
            "question": ""
        },
        {
            "title": "Xulosa",
            "body": "",
            "question": image_text["question"]
        }
    ]
