from src.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, BigInteger, ForeignKey, Boolean, text

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.models.vacancy import JobVacancy, Internship, OneTimeTask, OpportunitiesGrants

class Country(Base):
    __tablename__ = "country"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    en: Mapped[str | None] = mapped_column(String(255))
    name: Mapped[str | None] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))
    time_zoneutc: Mapped[str | None] = mapped_column(String(255))

    regions: Mapped[list["Region"]] = relationship(back_populates="country", lazy="selectin")

    job_vacancies: Mapped[list["JobVacancy"]] = relationship(back_populates="country", lazy="selectin")
    internships: Mapped[list["Internship"]] = relationship(back_populates="country", lazy="selectin")
    one_time_tasks: Mapped[list["OneTimeTask"]] = relationship(back_populates="country", lazy="selectin")
    opportunities_grants: Mapped[list["OpportunitiesGrants"]] = relationship(back_populates="country", lazy="selectin")

class Region(Base):
    __tablename__ = "region"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str | None] = mapped_column(String(255))
    country_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("country.id"), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))

    country: Mapped["Country"] = relationship(back_populates="regions", lazy="selectin")

    job_vacancies: Mapped[list["JobVacancy"]] = relationship(back_populates="region", lazy="selectin")
    internships: Mapped[list["Internship"]] = relationship(back_populates="region", lazy="selectin")
    one_time_tasks: Mapped[list["OneTimeTask"]] = relationship(back_populates="region", lazy="selectin")
    opportunities_grants: Mapped[list["OpportunitiesGrants"]] = relationship(back_populates="region", lazy="selectin")