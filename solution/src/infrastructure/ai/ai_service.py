import json
import os
import tempfile
from dataclasses import dataclass
from json import JSONDecodeError
from typing import TypeVar, cast

import aiohttp
from fastapi.responses import FileResponse
from src.application.ai.dtos import (
    GeneratedAdResponse,
    ImageDescriptionResponse,
    ModerationResponse,
)
from src.core.settings import Settings
from src.domain.ai.exceptions import (
    AIAuthenticationError,
    AIConnectionError,
    AIContentModerationError,
    AIImageGenerationError,
    AIInvalidResponseFormat,
    AIRateLimitError,
    AIRequestError,
    AIResponseParsingError,
)

T = TypeVar("T", GeneratedAdResponse, ModerationResponse, ImageDescriptionResponse)


@dataclass
class AIPrompts:
    AD_GENERATION = """Ты - опытный копирайтер в рекламном агентстве {advertiser_name}. Сгенерируй креативное рекламное объявление для следующего продукта: {ad_title}

Требования к рекламе:
- Текст должен быть современным и технологичным
- Подчеркни инновационность и уникальность продукта
- Используй трендовые слова и выражения из мира технологий
- Добавь элемент эксклюзивности или срочности
- Длина текста: максимум 2-3 предложения
- Стиль: динамичный и энергичный
- Упомяни бренд {advertiser_name} если это уместно

Сделай текст таким, чтобы он привлекал внимание и вызывал желание немедленно узнать больше о продукте.

Важно: Верни ответ строго в следующем формате JSON:
{{"generated_text": "текст сгенерированной рекламы"}}"""

    MODERATION_CHECK = """Ты - профессиональный модератор контента. Проанализируй следующий текст на наличие запрещенного содержания:

{text}

Проведи тщательный анализ по трем категориям и верни результат строго в следующем формате JSON:
{{"profanity_analysis": "объяснение почему такая оценка для нецензурной лексики",
  "profanity_probability": 0.XX,
  "profanity": true/false,
  "offensive_analysis": "объяснение почему такая оценка для оскорбительного контента",
  "offensive_probability": 0.XX,
  "offensive": true/false,
  "inappropriate_analysis": "объяснение почему такая оценка для неприемлемого контента",
  "inappropriate_probability": 0.XX,
  "inappropriate": true/false}}

Где 0.XX - это вероятность от 0.00 до 1.00, где:
0.00-0.30 - низкая вероятность
0.31-0.70 - средняя вероятность
0.71-1.00 - высокая вероятность

Подробные критерии оценки для каждой категории:

1. profanity (нецензурная лексика):
   - Мат и нецензурные выражения
   - Завуалированная нецензурная лексика
   - Грубые просторечные выражения

2. offensive (оскорбительный контент):
   - Прямые оскорбления и унижения
   - Дискриминация по любому признаку
   - Агрессивные высказывания
   - Призывы к насилию
   - Угрозы

3. inappropriate (неприемлемый контент):
   - Сексуальный подтекст
   - Намеки на нелегальную деятельность
   - Пропаганда опасного поведения

Важно: 
- Анализируй текст максимально объективно
- Для каждой категории укажи вероятность и подробное объяснение своей оценки
- Если вероятность выше 0.70, устанавливай true для этой категории
- В объяснении укажи конкретные слова или фразы, которые повлияли на оценку"""


class AIService:
    def __init__(self, settings: Settings):
        self.api_key = settings.ai_api_key
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = "google/gemini-2.0-flash-lite-preview-02-05:free"
        self.prompts = AIPrompts()
        self.settings = settings

    async def _make_api_request(
        self, prompt: str, expected_fields: list[str], response_type: type[T]
    ) -> T:
        try:
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.post(
                        url=self.api_url,
                        headers={
                            "Authorization": f"Bearer {self.api_key}",
                            "Content-Type": "application/json",
                        },
                        json={
                            "model": self.model,
                            "messages": [
                                {
                                    "role": "user",
                                    "content": [{"type": "text", "text": prompt}],
                                }
                            ],
                        },
                    ) as response:
                        if response.status == 401:
                            raise AIAuthenticationError(
                                "Неверный API ключ или аутентификация не удалась"
                            )
                        elif response.status == 429:
                            raise AIRateLimitError()
                        elif response.status != 200:
                            error_text = await response.text()
                            raise AIRequestError(
                                f"Запрос API не выполнен: {error_text}"
                            )

                        try:
                            data = await response.json()
                        except JSONDecodeError as e:
                            raise AIResponseParsingError(
                                f"Не удалось разобрать ответ API: {str(e)}"
                            )

                        try:
                            ai_response = data["choices"][0]["message"]["content"]
                        except (KeyError, IndexError) as e:
                            raise AIInvalidResponseFormat(
                                f"Непредвиденная структура ответа: {str(e)}"
                            )

                        cleaned_response = ai_response.strip()
                        cleaned_response = (
                            cleaned_response.replace("```json", "")
                            .replace("```", "")
                            .strip()
                        )

                        try:
                            response_json = json.loads(cleaned_response)
                        except JSONDecodeError as e:
                            raise AIResponseParsingError(
                                f"Не удалось разобрать ответ API: {str(e)}"
                            )

                        return cast(T, response_json)

                except aiohttp.ClientError as e:
                    raise AIConnectionError(
                        f"Не удалось подключиться к сервису AI: {str(e)}"
                    )

        except Exception as e:
            if isinstance(
                e,
                (
                    AIAuthenticationError,
                    AIConnectionError,
                    AIContentModerationError,
                    AIImageGenerationError,
                    AIInvalidResponseFormat,
                    AIRateLimitError,
                    AIRequestError,
                    AIResponseParsingError,
                ),
            ):
                raise e
            raise AIRequestError(f"Непредвиденная ошибка при запросе AI: {str(e)}")

    async def generate_ad(
        self, advertiser_name: str, ad_title: str
    ) -> GeneratedAdResponse:
        prompt = self.prompts.AD_GENERATION.format(
            advertiser_name=advertiser_name, ad_title=ad_title
        )
        return await self._make_api_request(
            prompt, ["generated_text"], GeneratedAdResponse
        )

    async def check_forbidden_words(self, text: str) -> ModerationResponse:
        prompt = self.prompts.MODERATION_CHECK.format(text=text)
        return await self._make_api_request(
            prompt, ["profanity", "offensive", "inappropriate"], ModerationResponse
        )

    async def generate_image(self, ad_title: str, ad_text: str) -> FileResponse:
        image_prompt = f"""Create a focused, single-subject advertising image description for {ad_title}:
        The image should highlight one key element from this advertising text: {ad_text}
        
        Requirements:
        - Feature one clear focal point or subject
        - Use dramatic lighting to emphasize the main subject
        - Keep the background simple and minimal
        - Ensure the subject fills 60-70% of the frame
        - Remove any distracting elements
        - Create strong visual impact through isolation
        
        Important: Return the response strictly in the following JSON format:
        {{"image_description": "detailed description of the image"}}"""

        try:
            description_response = await self._make_api_request(
                image_prompt, ["image_description"], ImageDescriptionResponse
            )
            image_description = description_response["image_description"]

            cloudflare_url = f"https://api.cloudflare.com/client/v4/accounts/{self.settings.cloudflare_account_id}/ai/run/{self.settings.cloudflare_model}"

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url=cloudflare_url,
                    headers={
                        "Authorization": f"Bearer {self.settings.cloudflare_api_token}",
                        "Content-Type": "application/json",
                    },
                    json={"prompt": image_description},
                ) as response:
                    if response.status == 401:
                        raise AIAuthenticationError(
                            "Неверные учетные данные Cloudflare"
                        )
                    elif response.status == 429:
                        raise AIRateLimitError("Превышен лимит API Cloudflare")
                    elif response.status != 200:
                        error_text = await response.text()
                        raise AIImageGenerationError(
                            f"Не удалось сгенерировать изображение: {error_text}"
                        )

                    image_content = await response.read()

                    temp_dir = tempfile.gettempdir()
                    temp_file_path = os.path.join(
                        temp_dir, f"generated_ad_{ad_title.replace(' ', '_')}.png"
                    )

                    with open(temp_file_path, "wb") as f:
                        f.write(image_content)

                    return FileResponse(
                        temp_file_path,
                        media_type="image/png",
                        filename=f"generated_ad_{ad_title.replace(' ', '_')}.png",
                    )

        except Exception as e:
            if isinstance(
                e,
                (
                    AIAuthenticationError,
                    AIConnectionError,
                    AIImageGenerationError,
                    AIRateLimitError,
                ),
            ):
                raise e
            raise AIImageGenerationError(
                f"Не удалось сгенерировать изображение: {str(e)}"
            )
