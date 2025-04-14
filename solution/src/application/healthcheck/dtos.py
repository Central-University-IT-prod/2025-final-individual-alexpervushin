from pydantic import BaseModel


class HealthcheckResponse(BaseModel):
    status: str
