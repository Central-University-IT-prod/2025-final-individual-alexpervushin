from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from src.adapters.telegram.common.constants import (
    BACK_TEXT,
    CALLBACK_BACK_TO_MAIN,
    CALLBACK_CONFIRM,
    CALLBACK_SKIP,
    CANCEL_TEXT,
    CONFIRM_TEXT,
)

CAMPAIGN_MANAGEMENT_KEYBOARD = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="📝 Создать кампанию"),
            KeyboardButton(text="📋 Список кампаний"),
        ],
        [KeyboardButton(text=BACK_TEXT)],
    ],
    resize_keyboard=True,
)

CAMPAIGN_CREATION_KEYBOARD = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="⏭️ Пропустить"),
            KeyboardButton(text=BACK_TEXT),
        ]
    ],
    resize_keyboard=True,
)


def get_campaign_management_keyboard(campaign_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✏️ Редактировать", callback_data=f"edit_campaign:{campaign_id}"
                ),
                InlineKeyboardButton(
                    text="🗑️ Удалить", callback_data=f"delete_campaign:{campaign_id}"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🖼️ Изображение", callback_data=f"manage_image:{campaign_id}"
                ),
                InlineKeyboardButton(
                    text="📊 Статистика", callback_data=f"campaign_stats:{campaign_id}"
                ),
            ],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_campaigns")],
        ]
    )


def get_image_management_keyboard(campaign_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📤 Загрузить", callback_data=f"upload_image:{campaign_id}"
                ),
                InlineKeyboardButton(
                    text="❌ Удалить", callback_data=f"delete_image:{campaign_id}"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Назад", callback_data=f"back_to_campaign:{campaign_id}"
                )
            ],
        ]
    )


def get_campaign_edit_keyboard(campaign_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📝 Название", callback_data=f"edit_title:{campaign_id}"
                ),
                InlineKeyboardButton(
                    text="📄 Текст", callback_data=f"edit_text:{campaign_id}"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="💰 Стоимость", callback_data=f"edit_costs:{campaign_id}"
                ),
                InlineKeyboardButton(
                    text="🎯 Таргетинг", callback_data=f"edit_targeting:{campaign_id}"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Назад", callback_data=f"back_to_campaign:{campaign_id}"
                )
            ],
        ]
    )


def get_campaigns_list_keyboard(
    current_page: int, total_pages: int, has_prev: bool, has_next: bool
) -> InlineKeyboardMarkup:
    keyboard = []

    navigation = []
    if has_prev:
        navigation.append(
            InlineKeyboardButton(
                text="◀️", callback_data=f"campaigns_page:{current_page - 1}"
            )
        )
    navigation.append(
        InlineKeyboardButton(
            text=f"{current_page}/{total_pages}", callback_data="current_page"
        )
    )
    if has_next:
        navigation.append(
            InlineKeyboardButton(
                text="▶️", callback_data=f"campaigns_page:{current_page + 1}"
            )
        )

    keyboard.append(navigation)
    keyboard.append(
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")]
    )

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


CONFIRM_KEYBOARD = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text=CONFIRM_TEXT, callback_data=CALLBACK_CONFIRM),
            InlineKeyboardButton(text=CANCEL_TEXT, callback_data=CALLBACK_BACK_TO_MAIN),
        ]
    ]
)

SKIP_KEYBOARD = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="⏭️ Пропустить", callback_data=CALLBACK_SKIP),
        ]
    ]
)
