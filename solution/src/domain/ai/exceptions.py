from src.core.exceptions.base import BaseException


class AIError(BaseException):
    status_code = 500
    default_message = "An error occurred while processing the AI request"


class AIConnectionError(AIError):
    status_code = 503
    default_message = "Unable to connect to AI service. Please try again later."


class AIResponseParsingError(AIError):
    status_code = 500
    default_message = "Failed to parse AI service response"


class AIInvalidResponseFormat(AIError):
    status_code = 500
    default_message = "AI service returned an invalid response format"


class AIRequestError(AIError):
    status_code = 400
    default_message = "Failed to process AI request"


class AIImageGenerationError(AIError):
    status_code = 500
    default_message = "Failed to generate image"


class AIContentModerationError(AIError):
    status_code = 500
    default_message = "Failed to moderate content"


class AIRateLimitError(AIError):
    status_code = 429
    default_message = "AI service rate limit exceeded. Please try again later."


class AIAuthenticationError(AIError):
    status_code = 401
    default_message = "Failed to authenticate with AI service"
