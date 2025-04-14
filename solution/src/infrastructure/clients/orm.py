from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.core.models import SQLAlchemyBaseModel, SQLAlchemyTimestampMixin


class ClientModel(SQLAlchemyBaseModel, SQLAlchemyTimestampMixin):
    __tablename__ = "clients"

    login: Mapped[str] = mapped_column(String, nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    location: Mapped[str] = mapped_column(String, nullable=False)
    gender: Mapped[str] = mapped_column(String, nullable=False)

    unique_events = relationship(
        "UniqueEventModel", back_populates="client", cascade="all, delete-orphan"
    )
