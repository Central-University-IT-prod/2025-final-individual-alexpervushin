from dataclasses import dataclass

from src.core.entities.base_entity import BaseEntity


@dataclass
class ClientEntity(BaseEntity):
    login: str
    age: int
    location: str
    gender: str
