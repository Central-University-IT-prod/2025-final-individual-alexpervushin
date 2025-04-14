from typing import TypedDict


class MLScoreErrorMessages(TypedDict):
    update_failed: str
    invalid_format: str
    empty_score: str


class DbErrorMessages(TypedDict):
    advertiser_creation: str
    telegram_link: str
    advertiser_join: str
    ml_score_update: str
    campaign_creation: str
    campaign_update: str
    campaign_delete: str


class CampaignErrorMessages(TypedDict):
    invalid_title: str
    invalid_text: str
    invalid_limits: str
    invalid_costs: str
    invalid_dates: str
    invalid_targeting: str
    image_upload: str
    image_delete: str


class ErrorMessages(TypedDict):
    user_not_found: str
    not_registered: str
    empty_advertiser_name: str
    advertiser_creation_failed: str
    invalid_uuid: str
    advertiser_not_found: str
    invalid_score: str
    db_error: DbErrorMessages
    ml_score: MLScoreErrorMessages
    campaign: CampaignErrorMessages


class SuccessMessages(TypedDict):
    advertiser_created: str
    advertiser_joined: str
    ml_score_updated: str
    campaign_created: str
    campaign_updated: str
    campaign_deleted: str
    image_uploaded: str
    image_deleted: str


class PromptMessages(TypedDict):
    welcome: str
    enter_advertiser_name: str
    enter_advertiser_id: str
    enter_client_id: str
    enter_ml_score: str
    use_buttons: str
    uuid_format: str
    score_format: str
    campaign_title: str
    campaign_text: str
    campaign_limits: str
    campaign_costs: str
    campaign_dates: str
    campaign_targeting: str


class InfoMessages(TypedDict):
    advertiser_info: str
    campaign_info: str
    campaign_list: str


CREATE_ADVERTISER_TEXT = "🏢 Создать новую компанию"
JOIN_ADVERTISER_TEXT = "🤝 Присоединиться к компании"
GET_INFO_TEXT = "ℹ️ Информация о компании"
SET_ML_SCORE_TEXT = "📊 Настроить ML оценку"
BACK_TEXT = "⬅️ Назад"

CREATE_CAMPAIGN_TEXT = "📝 Создать кампанию"
LIST_CAMPAIGNS_TEXT = "📋 Список кампаний"
SKIP_TEXT = "⏭️ Пропустить"

EDIT_CAMPAIGN_TEXT = "✏️ Редактировать"
DELETE_CAMPAIGN_TEXT = "🗑️ Удалить"
MANAGE_IMAGE_TEXT = "🖼️ Изображение"
CAMPAIGN_STATS_TEXT = "📊 Статистика"

EDIT_TITLE_TEXT = "📝 Название"
EDIT_TEXT_TEXT = "📄 Текст"
EDIT_COSTS_TEXT = "💰 Стоимость"
EDIT_TARGETING_TEXT = "🎯 Таргетинг"

UPLOAD_IMAGE_TEXT = "📤 Загрузить"
DELETE_IMAGE_TEXT = "❌ Удалить"

PREV_PAGE_TEXT = "◀️"
NEXT_PAGE_TEXT = "▶️"
CONFIRM_TEXT = "✅ Да"
CANCEL_TEXT = "❌ Нет"

CALLBACK_EDIT_CAMPAIGN = "edit_campaign"
CALLBACK_DELETE_CAMPAIGN = "delete_campaign"
CALLBACK_MANAGE_IMAGE = "manage_image"
CALLBACK_CAMPAIGN_STATS = "campaign_stats"
CALLBACK_UPLOAD_IMAGE = "upload_image"
CALLBACK_DELETE_IMAGE = "delete_image"
CALLBACK_EDIT_TITLE = "edit_title"
CALLBACK_EDIT_TEXT = "edit_text"
CALLBACK_EDIT_COSTS = "edit_costs"
CALLBACK_EDIT_TARGETING = "edit_targeting"
CALLBACK_CAMPAIGNS_PAGE = "campaigns_page"
CALLBACK_BACK_TO_CAMPAIGN = "back_to_campaign"
CALLBACK_BACK_TO_CAMPAIGNS = "back_to_campaigns"
CALLBACK_BACK_TO_MAIN = "back_to_main"
CALLBACK_CONFIRM = "confirm"
CALLBACK_CANCEL = "cancel"
CALLBACK_SKIP = "skip"

ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/gif", "image/webp"]
MAX_IMAGE_SIZE = 5 * 1024 * 1024

DEFAULT_PAGE_SIZE = 10
MAX_PAGE_SIZE = 50


CAMPAIGNS_TEXT = "🎯 Кампании"
ADVERTISERS_TEXT = "👥 Рекламодатели"
