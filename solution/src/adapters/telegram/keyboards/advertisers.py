from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from src.adapters.telegram.common.constants import (
    BACK_TEXT,
    CREATE_ADVERTISER_TEXT,
    GET_INFO_TEXT,
    JOIN_ADVERTISER_TEXT,
    SET_ML_SCORE_TEXT,
)

MAIN_KEYBOARD = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text=CREATE_ADVERTISER_TEXT),
            KeyboardButton(text=JOIN_ADVERTISER_TEXT),
        ],
        [
            KeyboardButton(text=GET_INFO_TEXT),
            KeyboardButton(text=SET_ML_SCORE_TEXT),
        ],
    ],
    resize_keyboard=True,
)

BACK_KEYBOARD = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text=BACK_TEXT)]],
    resize_keyboard=True,
)
