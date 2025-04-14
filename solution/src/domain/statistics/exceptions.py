from src.core.exceptions.base import BaseException


class DuplicateClickError(BaseException):
    status_code = 400
    default_message = "Click already registered for this client and campaign"


class StatisticsRepositoryError(BaseException):
    status_code = 500
    default_message = "Database error occurred while processing statistics data"


class NoImpressionError(BaseException):
    status_code = 400
    default_message = "Cannot register click without prior impression"


class ClicksLimitReachedError(BaseException):
    status_code = 400
    default_message = "Clicks limit has been reached for this campaign"
