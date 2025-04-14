import uuid

from sqlalchemy import BigInteger, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.core.models import SQLAlchemyBaseModel, SQLAlchemyTimestampMixin


class AdvertiserModel(SQLAlchemyBaseModel, SQLAlchemyTimestampMixin):
    __tablename__ = "advertisers"

    name: Mapped[str] = mapped_column(String, nullable=False)


class MLScoreModel(SQLAlchemyBaseModel, SQLAlchemyTimestampMixin):
    __tablename__ = "ml_scores"

    client_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("clients.id"),
        nullable=False,
    )
    advertiser_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("advertisers.id"),
        nullable=False,
    )
    score: Mapped[int] = mapped_column(Integer, nullable=False)

    client = relationship("ClientModel", backref="ml_scores")
    advertiser = relationship("AdvertiserModel", backref="ml_scores")


class TelegramAdvertiserModel(SQLAlchemyBaseModel, SQLAlchemyTimestampMixin):
    __tablename__ = "telegram_advertisers"

    telegram_id: Mapped[int] = mapped_column(BigInteger, nullable=False, unique=True)
    advertiser_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("advertisers.id"),
        nullable=False,
    )

    advertiser = relationship("AdvertiserModel", backref="telegram_users")
