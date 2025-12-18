from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Integer, String, BigInteger, func
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from src.database import Base
from src.models.locations import Country, Region
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.models.locations import Country, Region
    from models.industry import Industry

class Users(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, nullable=False, unique=True, index=True)
    language_code: Mapped[str | None] = mapped_column(String(12), nullable=True)

    full_name: Mapped[str | None] = mapped_column(String(256), nullable=True)
    contact: Mapped[str | None] = mapped_column(String(500), nullable=True)

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    client: Mapped["Clients"] = relationship(back_populates="user", uselist=False, lazy="joined")
    

class Clients(Base):
    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    company_name: Mapped[str | None] = mapped_column(String(300), nullable=True)

    industry_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey('industry.id'), nullable=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), unique=True)
    country_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("country.id"))
    region_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("region.id"))

    user: Mapped["Users"] = relationship(back_populates="client", lazy="joined")
    country: Mapped["Country"] = relationship(lazy="selectin")
    region: Mapped["Region"] = relationship(lazy="selectin")
    industry: Mapped["Industry"] = relationship(
        back_populates="client",
        lazy="selectin",
    )