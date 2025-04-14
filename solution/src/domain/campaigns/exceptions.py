from src.core.exceptions.base import BaseException


class CampaignNotFoundException(BaseException):
    status_code = 404
    default_message = "Campaign not found"


class CampaignRepositoryError(BaseException):
    status_code = 500
    default_message = "Campaign repository error"


class CampaignForbiddenError(BaseException):
    status_code = 403
    default_message = "Campaign does not belong to this advertiser"


class CampaignImageUploadError(BaseException):
    status_code = 500
    default_message = "Failed to upload campaign image"


class CampaignModerationError(BaseException):
    status_code = 400
    default_message = "Campaign moderation error"
