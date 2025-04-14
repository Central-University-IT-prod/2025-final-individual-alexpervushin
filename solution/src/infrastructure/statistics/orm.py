from typing import Optional
from uuid import UUID

import sqlalchemy
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.core.models import SQLAlchemyBaseModel, SQLAlchemyTimestampMixin


class UniqueEventModel(SQLAlchemyBaseModel, SQLAlchemyTimestampMixin):
    __tablename__ = "unique_events"

    campaign_id: Mapped[UUID] = mapped_column(
        sqlalchemy.UUID(as_uuid=True),
        ForeignKey("campaigns.id", ondelete="CASCADE"),
        nullable=False,
    )
    client_id: Mapped[UUID] = mapped_column(
        sqlalchemy.UUID(as_uuid=True),
        ForeignKey("clients.id", ondelete="CASCADE"),
        nullable=False,
    )
    event_type: Mapped[str] = mapped_column(
        sqlalchemy.String(length=20), nullable=False
    )
    date: Mapped[int] = mapped_column(
        sqlalchemy.Integer,
        nullable=False,
    )
    rating: Mapped[Optional[int]] = mapped_column(
        sqlalchemy.Integer,
        nullable=True,
    )
    comment: Mapped[Optional[str]] = mapped_column(
        sqlalchemy.String(length=1000),
        nullable=True,
    )

    campaign = relationship("CampaignModel", back_populates="unique_events")
    client = relationship("ClientModel", back_populates="unique_events")

    __table_args__ = (
        UniqueConstraint(
            "campaign_id", "client_id", "event_type", name="uix_campaign_client_event"
        ),
    )
