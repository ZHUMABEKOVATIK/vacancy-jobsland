from sqlalchemy import String, ForeignKey, BigInteger, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from datetime import datetime
from src.database import Base
from src.models.locations import Country, Region

class Channels(Base):
    __tablename__ = "channels"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    country_id: Mapped[int] = mapped_column(ForeignKey("country.id"), nullable=False)
    region_id: Mapped[int | None] = mapped_column(ForeignKey("region.id"), nullable=True)
    channel_url: Mapped[str] = mapped_column(String, nullable=False)

    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime] = mapped_column(default=func.now(), onupdate=func.now())

    country: Mapped["Country"] = relationship(lazy="selectin")
    region: Mapped["Region"] = relationship(lazy="selectin")