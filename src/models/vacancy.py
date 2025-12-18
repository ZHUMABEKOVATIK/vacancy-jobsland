from sqlalchemy import Index, String, ForeignKey, BigInteger, func, Boolean, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Enum as SQLEnum
from datetime import datetime
import enum
from typing import TYPE_CHECKING

from src.database import Base
from src.models.users import Users

if TYPE_CHECKING:
    from src.models.locations import Country, Region

class StatusEnum(enum.Enum):
    NEW = "NEW"
    IN_REVIEW = "IN_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

class JobVacancy(Base):
    __tablename__ = "job_vacancies"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    country_id: Mapped[int] = mapped_column(ForeignKey("country.id"), nullable=False, index=True)
    region_id: Mapped[int] = mapped_column(ForeignKey("region.id"), nullable=True, index=True)

    position_title: Mapped[str] = mapped_column(String, nullable=False) # Lawazım
    organization_name: Mapped[str] = mapped_column(String(255), nullable=True) # Mekeme
    address: Mapped[str] = mapped_column(String(255), nullable=False) # Mánzil
    requirements: Mapped[str] = mapped_column(String, nullable=False) # Talaplar
    duties: Mapped[str] = mapped_column(String, nullable=True) # Májburiyatlar
    work_schedule: Mapped[str] = mapped_column(String, nullable=False) # Jumıs waqıtı/formatı:
    salary: Mapped[str] = mapped_column(String, nullable=False) # Aylıq
    contact: Mapped[str] = mapped_column(String, nullable=False) # Baylanıs
    additional_info: Mapped[str] = mapped_column(String, nullable=True) # Qosımsha

    status: Mapped[StatusEnum] = mapped_column(SQLEnum(StatusEnum, name="status_type"), server_default=text("'NEW'"), index=True)
    reject_reason: Mapped[str] = mapped_column(String, nullable=True)
    is_delete: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))

    group_chat_id: Mapped[int] = mapped_column(BigInteger, nullable=True)
    group_message_id: Mapped[int] = mapped_column(BigInteger, nullable=True)
    channel_chat_id: Mapped[int] = mapped_column(BigInteger, nullable=True)
    channel_message_id: Mapped[int] = mapped_column(BigInteger, nullable=True)
    moderator_id: Mapped[int] = mapped_column(BigInteger, nullable=True)

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    country: Mapped["Country"] = relationship(lazy="selectin", back_populates="job_vacancies")
    region: Mapped["Region"] = relationship(lazy="selectin", back_populates="job_vacancies")
    user: Mapped["Users"] = relationship(lazy="selectin", foreign_keys=[author_id])


class Internship(Base):
    __tablename__ = "internship"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    country_id: Mapped[int] = mapped_column(ForeignKey("country.id"), nullable=False, index=True)
    region_id: Mapped[int] = mapped_column(ForeignKey("region.id"), nullable=True, index=True)

    position_title: Mapped[str] = mapped_column(String, nullable=False) # Lawazım
    organization_name: Mapped[str] = mapped_column(String(255), nullable=True) # Mekeme
    requirements: Mapped[str] = mapped_column(String, nullable=False) # Talaplar
    duties: Mapped[str] = mapped_column(String, nullable=False) # Májburiyatlar
    conditions: Mapped[str] = mapped_column(String, nullable=True) # Shárayatlar
    address: Mapped[str] = mapped_column(String(255), nullable=False) # Mánzil hám format
    salary: Mapped[str] = mapped_column(String, nullable=False) # Aylıq
    contact: Mapped[str] = mapped_column(String, nullable=False) # Baylanıs
    additional_info: Mapped[str] = mapped_column(String, nullable=True) # Qosımsha

    status: Mapped[StatusEnum] = mapped_column(SQLEnum(StatusEnum, name="status_type"), server_default=text("'NEW'"), index=True)
    reject_reason: Mapped[str] = mapped_column(String, nullable=True)
    is_delete: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))

    group_chat_id: Mapped[int] = mapped_column(BigInteger, nullable=True)
    group_message_id: Mapped[int] = mapped_column(BigInteger, nullable=True)
    channel_chat_id: Mapped[int] = mapped_column(BigInteger, nullable=True)
    channel_message_id: Mapped[int] = mapped_column(BigInteger, nullable=True)
    moderator_id: Mapped[int] = mapped_column(BigInteger, nullable=True)

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    country: Mapped["Country"] = relationship(lazy="selectin", back_populates="internships")
    region: Mapped["Region"] = relationship(lazy="selectin", back_populates="internships")
    user: Mapped["Users"] = relationship(lazy="selectin", foreign_keys=[author_id])


class OneTimeTask(Base):
    __tablename__ = "one_time_task"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    country_id: Mapped[int] = mapped_column(ForeignKey("country.id"), nullable=False, index=True)
    region_id: Mapped[int] = mapped_column(ForeignKey("region.id"), nullable=True, index=True)

    who_needed: Mapped[str] = mapped_column(String, nullable=False)
    task_description: Mapped[str] = mapped_column(String, nullable=False)
    deadline: Mapped[str] = mapped_column(String, nullable=True)
    salary: Mapped[str] = mapped_column(String, nullable=False)
    contact: Mapped[str] = mapped_column(String, nullable=False)
    address: Mapped[str] = mapped_column(String(255), nullable=True)
    additional_info: Mapped[str] = mapped_column(String, nullable=True)

    status: Mapped[StatusEnum] = mapped_column(SQLEnum(StatusEnum, name="status_type"), server_default=text("'NEW'"), index=True)
    reject_reason: Mapped[str] = mapped_column(String, nullable=True)
    is_delete: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))

    group_chat_id: Mapped[int] = mapped_column(BigInteger, nullable=True)
    group_message_id: Mapped[int] = mapped_column(BigInteger, nullable=True)
    channel_chat_id: Mapped[int] = mapped_column(BigInteger, nullable=True)
    channel_message_id: Mapped[int] = mapped_column(BigInteger, nullable=True)
    moderator_id: Mapped[int] = mapped_column(BigInteger, nullable=True)

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    country: Mapped["Country"] = relationship(lazy="selectin", back_populates="one_time_tasks")
    region: Mapped["Region"] = relationship(lazy="selectin", back_populates="one_time_tasks")
    user: Mapped["Users"] = relationship(lazy="selectin", foreign_keys=[author_id])


class OpportunitiesGrants(Base):
    __tablename__ = "opportunities_grants"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    country_id: Mapped[int] = mapped_column(ForeignKey("country.id"), nullable=False, index=True)
    region_id: Mapped[int] = mapped_column(ForeignKey("region.id"), nullable=True, index=True)

    img_path: Mapped[str | None] = mapped_column(String(256), nullable=True)
    content: Mapped[str] = mapped_column(String, nullable=False)
    contact: Mapped[str] = mapped_column(String(256), nullable=False)

    status: Mapped[StatusEnum] = mapped_column(SQLEnum(StatusEnum, name="status_type"), server_default=text("'NEW'"), index=True)
    reject_reason: Mapped[str] = mapped_column(String, nullable=True)
    is_delete: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))

    group_chat_id: Mapped[int] = mapped_column(BigInteger, nullable=True)
    group_message_id: Mapped[int] = mapped_column(BigInteger, nullable=True)
    channel_chat_id: Mapped[int] = mapped_column(BigInteger, nullable=True)
    channel_message_id: Mapped[int] = mapped_column(BigInteger, nullable=True)
    moderator_id: Mapped[int] = mapped_column(BigInteger, nullable=True)

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    country: Mapped["Country"] = relationship(lazy="selectin", back_populates="opportunities_grants")
    region: Mapped["Region"] = relationship(lazy="selectin", back_populates="opportunities_grants")
    user: Mapped["Users"] = relationship(lazy="selectin", foreign_keys=[author_id])