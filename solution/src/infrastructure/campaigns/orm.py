from uuid import UUID

from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.core.models import SQLAlchemyBaseModel, SQLAlchemyTimestampMixin


class CampaignModel(SQLAlchemyBaseModel, SQLAlchemyTimestampMixin):
    __tablename__ = "campaigns"

    advertiser_id: Mapped[UUID] = mapped_column(
        ForeignKey("advertisers.id"),
        nullable=False,
    )
    image_url: Mapped[str | None] = mapped_column(String, nullable=True)
    impressions_limit: Mapped[int] = mapped_column(Integer, nullable=False)
    clicks_limit: Mapped[int] = mapped_column(Integer, nullable=False)
    cost_per_impression: Mapped[float] = mapped_column(Float, nullable=False)
    cost_per_click: Mapped[float] = mapped_column(Float, nullable=False)
    ad_title: Mapped[str] = mapped_column(String, nullable=False)
    ad_text: Mapped[str] = mapped_column(String, nullable=False)
    start_date: Mapped[int] = mapped_column(Integer, nullable=False)
    end_date: Mapped[int] = mapped_column(Integer, nullable=False)
    gender: Mapped[str | None] = mapped_column(String, nullable=True)
    age_from: Mapped[int | None] = mapped_column(Integer, nullable=True)
    age_to: Mapped[int | None] = mapped_column(Integer, nullable=True)
    location: Mapped[str | None] = mapped_column(String, nullable=True)

    advertiser = relationship("AdvertiserModel", backref="campaigns")
    unique_events = relationship(
        "UniqueEventModel", back_populates="campaign", cascade="all, delete-orphan"
    )
