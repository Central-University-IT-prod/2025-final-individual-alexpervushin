from src.core.exceptions.base import BaseException


class ClientNotFoundException(BaseException):
    status_code = 404
    default_message = "Client not found"


class ClientRepositoryError(BaseException):
    status_code = 500
    default_message = "Database error occurred while processing client data"
