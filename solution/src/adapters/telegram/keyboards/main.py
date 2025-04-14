from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from src.adapters.telegram.common.constants import ADVERTISERS_TEXT, CAMPAIGNS_TEXT

MAIN_KEYBOARD = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text=CAMPAIGNS_TEXT),
            KeyboardButton(text=ADVERTISERS_TEXT),
        ],
    ],
    resize_keyboard=True,
)
