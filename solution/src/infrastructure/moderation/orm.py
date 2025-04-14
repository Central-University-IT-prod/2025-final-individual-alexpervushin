from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from src.core.models import SQLAlchemyBaseModel, SQLAlchemyTimestampMixin


class ForbiddenWordsModel(SQLAlchemyBaseModel, SQLAlchemyTimestampMixin):
    __tablename__ = "forbidden_words"

    word: Mapped[str] = mapped_column(String, nullable=False)
