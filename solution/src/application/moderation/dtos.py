from typing import Dict, Optional, Union

from pydantic import BaseModel


class ForbiddenWord(BaseModel):
    word: str


class AIModerationResponse(BaseModel):
    profanity: bool
    offensive: bool
    inappropriate: bool


class ModerationResponse(BaseModel):
    contains_forbidden_words: bool
    source: str
    details: Optional[Union[Dict[str, bool], AIModerationResponse]] = None

