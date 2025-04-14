from datetime import datetime
from uuid import UUID

import sqlalchemy
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from src.core.db import Base


class SQLAlchemyBaseModel(Base):
    __abstract__ = True

    id: Mapped[UUID] = mapped_column(
        sqlalchemy.UUID(as_uuid=True),
        primary_key=True,
        nullable=False,
    )


class SQLAlchemyTimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        sqlalchemy.DateTime(timezone=True),
        default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        sqlalchemy.DateTime(timezone=True),
        default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
