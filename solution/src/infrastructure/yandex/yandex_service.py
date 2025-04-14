import json
from typing import Any, Dict, List, Optional
from uuid import UUID

import aiohttp
from src.core.settings import Settings
from src.domain.campaigns.entities import CampaignEntity
from src.domain.campaigns.interfaces import YandexDirectServiceProtocol


class YandexDirectService(YandexDirectServiceProtocol):
    CAMPAIGNS_URL = "https://api-sandbox.direct.yandex.com/json/v5/campaigns"
    ADS_URL = "https://api-sandbox.direct.yandex.com/json/v5/ads"

    def __init__(self, settings: Settings, token: Optional[str] = None):
        self.settings = settings
        self.token = token or settings.yandex_token
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept-Language": "ru",
        }

    async def _make_request(
        self, url: str, body: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        try:
            json_body = json.dumps(body, ensure_ascii=False).encode("utf8")
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url, data=json_body, headers=self.headers
                ) as response:
                    if response.status != 200:
                        return None

                    data = await response.json()
                    if data.get("error"):
                        error = data["error"]
                        return None

                    return data

        except aiohttp.ClientError:
            return None
        except json.JSONDecodeError:
            return None
        except Exception:
            return None

    async def get_campaign_entities(
        self, token: Optional[str], advertiser_id: UUID
    ) -> List[CampaignEntity]:
        if token:
            self.token = token
            self.headers["Authorization"] = f"Bearer {self.token}"

        campaigns_body = {
            "method": "get",
            "params": {
                "SelectionCriteria": {},
                "FieldNames": [
                    "Id",
                    "Name",
                    "Type",
                    "StartDate",
                    "EndDate",
                ],
            },
        }

        campaigns_data = await self._make_request(self.CAMPAIGNS_URL, campaigns_body)
        if not campaigns_data or "result" not in campaigns_data:
            return []

        campaign_data = campaigns_data["result"].get("Campaigns", [])
        campaign_ids = [camp["Id"] for camp in campaign_data]

        if campaign_ids:
            ads_body = {
                "method": "get",
                "params": {
                    "SelectionCriteria": {"CampaignIds": campaign_ids},
                    "FieldNames": ["Id", "Title", "Text", "CampaignId"],
                },
            }
            ads_data = await self._make_request(self.ADS_URL, ads_body)
            ads_by_campaign = {}
            if ads_data and "result" in ads_data:
                for ad in ads_data["result"].get("Ads", []):
                    campaign_id = ad.get("CampaignId")
                    if campaign_id:
                        if campaign_id not in ads_by_campaign:
                            ads_by_campaign[campaign_id] = []
                        ads_by_campaign[campaign_id].append(ad)

        entities = []
        for camp in campaign_data:
            campaign_id = camp["Id"]
            campaign_ads = ads_by_campaign.get(campaign_id, [])
            ad_text = ""
            if campaign_ads:
                first_ad = campaign_ads[0]
                ad_text = (
                    f"{first_ad.get('Title', '')} {first_ad.get('Text', '')}".strip()
                )

            try:
                start_date = int(camp.get("StartDate", "").replace("-", ""))
                end_date = (
                    int(camp.get("EndDate", "").replace("-", ""))
                    if camp.get("EndDate")
                    else start_date + 30
                )

                entity = CampaignEntity(
                    id=UUID(int=int(campaign_id)),
                    advertiser_id=advertiser_id,
                    impressions_limit=10000,
                    clicks_limit=1000,
                    cost_per_impression=0.1,
                    cost_per_click=1.0,
                    ad_title=camp.get("Name", ""),
                    ad_text=ad_text,
                    start_date=start_date,
                    end_date=end_date,
                    image_url=None,
                    gender=None,
                    age_from=None,
                    age_to=None,
                    location=None,
                )
                entities.append(entity)
            except (KeyError, ValueError):
                continue

        return entities
