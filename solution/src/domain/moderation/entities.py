from dataclasses import dataclass
from typing import Dict, Optional, Union

from src.application.ai.dtos import ModerationResponse
from src.core.entities.base_entity import BaseEntity


@dataclass
class ForbiddenWordsEntity(BaseEntity):
    word: str


@dataclass
class ModerationResultEntity(BaseEntity):
    contains_forbidden_words: bool
    source: str
    details: Optional[Union[Dict[str, bool], ModerationResponse]] = None
