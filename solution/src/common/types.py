from typing import NewType
from uuid import UUID

ClientId = NewType("ClientId", UUID)
AdvertiserId = NewType("AdvertiserId", UUID)
CampaignId = NewType("CampaignId", UUID)

EVENT_TYPE_IMPRESSION = "impression"
EVENT_TYPE_CLICK = "click"