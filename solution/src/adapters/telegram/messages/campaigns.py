from typing import TypedDict


class CampaignErrorMessages(TypedDict):
    campaign_not_found: str
    invalid_campaign_id: str
    creation_failed: str
    update_failed: str
    delete_failed: str
    image_upload_failed: str
    image_delete_failed: str
    invalid_date: str
    invalid_limits: str
    invalid_costs: str
    invalid_targeting: str
    invalid_title: str
    invalid_text: str
    user_not_found: str
    not_registered: str


class CampaignSuccessMessages(TypedDict):
    created: str
    updated: str
    deleted: str
    image_uploaded: str
    image_deleted: str
    targeting_updated: str


class CampaignPromptMessages(TypedDict):
    welcome_campaigns: str
    create_campaign: str
    enter_title: str
    enter_text: str
    enter_impressions_limit: str
    enter_clicks_limit: str
    enter_cost_per_impression: str
    enter_cost_per_click: str
    enter_start_date: str
    enter_end_date: str
    enter_targeting: str
    enter_gender: str
    enter_age_from: str
    enter_age_to: str
    enter_location: str
    upload_image: str
    confirm_delete: str
    confirm_delete_image: str
    confirm_targeting: str
    confirm_creation: str
    choose_edit_field: str
    campaign_management: str


class CampaignInfoMessages(TypedDict):
    campaign_details: str
    campaign_list: str
    campaign_list_item: str
    no_campaigns: str
    targeting_info: str


class Messages:
    ERROR: CampaignErrorMessages = {
        "campaign_not_found": "❌ Рекламная кампания не найдена",
        "invalid_campaign_id": "❌ Неверный формат ID кампании",
        "creation_failed": "❌ Не удалось создать рекламную кампанию",
        "update_failed": "❌ Не удалось обновить рекламную кампанию",
        "delete_failed": "❌ Не удалось удалить рекламную кампанию",
        "image_upload_failed": "❌ Не удалось загрузить изображение",
        "image_delete_failed": "❌ Не удалось удалить изображение",
        "invalid_date": "❌ Неверный формат даты",
        "invalid_limits": "❌ Лимиты показов и кликов должны быть положительными числами",
        "invalid_costs": "❌ Стоимость показов и кликов должна быть положительным числом",
        "invalid_targeting": "❌ Неверный формат параметров таргетинга",
        "invalid_title": "❌ Название кампании не может быть пустым",
        "invalid_text": "❌ Текст объявления не может быть пустым",
        "user_not_found": "❌ Пользователь не найден",
        "not_registered": "❌ Вы не зарегистрированы как рекламодатель. Пожалуйста, зарегистрируйтесь",
    }

    SUCCESS: CampaignSuccessMessages = {
        "created": (
            "✅ Рекламная кампания успешно создана!\n\n"
            "Название: {title}\n"
            "ID кампании: {id}\n"
            "Период: {start_date} - {end_date}\n"
            "Лимиты: {impressions_limit} показов, {clicks_limit} кликов\n"
            "Стоимость: {cost_per_impression}₽ за показ, {cost_per_click}₽ за клик"
        ),
        "updated": "✅ Рекламная кампания успешно обновлена",
        "deleted": "✅ Рекламная кампания успешно удалена",
        "image_uploaded": "✅ Изображение успешно загружено\nURL: {image_url}",
        "image_deleted": "✅ Изображение успешно удалено",
        "targeting_updated": "✅ Настройки таргетинга успешно обновлены",
    }

    PROMPTS: CampaignPromptMessages = {
        "welcome_campaigns": "👋 Управление рекламными кампаниями\n\nВыберите действие:",
        "create_campaign": (
            "📝 Создание новой рекламной кампании\n\n"
            "Пожалуйста, следуйте инструкциям для заполнения всех необходимых данных."
        ),
        "enter_title": "Введите название рекламной кампании:",
        "enter_text": "Введите текст рекламного объявления:",
        "enter_impressions_limit": (
            "Введите лимит показов рекламного объявления\n:"
        ),
        "enter_clicks_limit": (
            "Введите лимит кликов по рекламному объявлению\n"
            "(целое положительное число):"
        ),
        "enter_cost_per_impression": (
            "Введите стоимость одного показа в рублях\n:"
        ),
        "enter_cost_per_click": (
            "Введите стоимость одного клика в рублях\n:"
        ),
        "enter_start_date": "Введите дату начала кампании\n",
        "enter_end_date": "Введите дату окончания кампании\n",
        "enter_targeting": (
            "Настройка таргетинга (опционально):\n\n"
            "Пол (MALE/FEMALE/ALL):\n"
            "Возраст от:\n"
            "Возраст до:\n"
            "Локация (текст):"
        ),
        "enter_gender": "Укажите пол целевой аудитории (MALE/FEMALE/ALL):",
        "enter_age_from": "Укажите минимальный возраст целевой аудитории:",
        "enter_age_to": "Укажите максимальный возраст целевой аудитории:",
        "enter_location": "Укажите локацию для таргетинга:",
        "upload_image": (
            "📎 Загрузите изображение для рекламной кампании\n"
            "Поддерживаемые форматы: JPEG, PNG, GIF, WEBP"
        ),
        "confirm_delete": "❗️ Вы уверены, что хотите удалить эту рекламную кампанию?",
        "confirm_delete_image": "❗️ Вы уверены, что хотите удалить изображение?",
        "confirm_targeting": (
            "Проверьте настройки таргетинга:\n\n"
            "Пол: {gender}\n"
            "Возраст: {age_from}-{age_to}\n"
            "Локация: {location}\n\n"
            "Всё верно?"
        ),
        "confirm_creation": "Проверьте данные и подтвердите создание рекламной кампании:",
        "choose_edit_field": "Выберите, что хотите изменить:",
        "campaign_management": "Управление рекламной кампанией:",
    }

    INFO: CampaignInfoMessages = {
        "campaign_details": (
            "📊 Информация о рекламной кампании\n\n"
            "ID: {id}\n"
            "Название: {title}\n"
            "Текст: {text}\n"
            "Период: {start_date} - {end_date}\n\n"
            "Лимиты:\n"
            "- Показы: {impressions_limit}\n"
            "- Клики: {clicks_limit}\n\n"
            "Стоимость:\n"
            "- За показ: {cost_per_impression}₽\n"
            "- За клик: {cost_per_click}₽\n\n"
            "Изображение: {image_url}\n\n"
            "{targeting_info}"
        ),
        "campaign_list": (
            "📑 Список рекламных кампаний\n\n"
            "Всего кампаний: {total}\n"
            "Страница {page} из {total_pages}\n\n"
            "{campaigns}"
        ),
        "campaign_list_item": ("🎯 Кампания: {title}\nID: {id}\nСтатус: {status}"),
        "no_campaigns": "У вас пока нет рекламных кампаний",
        "targeting_info": (
            "🎯 Таргетинг:\n"
            "- Пол: {gender}\n"
            "- Возраст: {age_from}-{age_to}\n"
            "- Локация: {location}"
        ),
    }
