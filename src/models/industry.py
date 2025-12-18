from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Integer, String, BigInteger

from typing import TYPE_CHECKING
from src.database import Base

if TYPE_CHECKING:
    from src.models.users import Clients

class Industry(Base):
    __tablename__ = "industry"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(256), nullable=False)

    client: Mapped[list["Clients"]] = relationship(
        back_populates="industry",
        lazy="selectin",
    )