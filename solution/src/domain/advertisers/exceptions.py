from src.core.exceptions.base import BaseException


class AdvertiserNotFoundException(BaseException):
    status_code = 404
    default_message = "Advertiser not found"


class AdvertiserRepositoryError(BaseException):
    status_code = 500
    default_message = "Database error occurred while processing advertiser data"


class TelegramLinkError(BaseException):
    status_code = 400
    default_message = "Error linking telegram account to advertiser"


class MLScoreRepositoryError(BaseException):
    status_code = 500
    default_message = "Database error occurred while processing ML score data"
