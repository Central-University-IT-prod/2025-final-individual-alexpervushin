from src.core.exceptions.base import BaseException


class TimeRepositoryError(BaseException):
    status_code = 500
    default_message = "Error occurred while processing time data"
