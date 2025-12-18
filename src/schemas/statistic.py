from pydantic import BaseModel, Field

class VacancyCard(BaseModel):
    code: str = Field(..., example="job_vacancies")
    title: str = Field(..., example="Вакансии")
    length: int = Field(..., example=437)
    icon: str = Field(..., example="MdWork")
    color: str = Field(..., example="#267fe9")
    approved: int = Field(..., example=5)
    rejected: int = Field(..., example=4)

class MonthStat(BaseModel):
    month: int = Field(..., example=1)
    value: int = Field(..., example=42)

class StatVacancyOut(BaseModel):
    data: list[VacancyCard]= Field(
        ...,
        description="List of statistic data (depends on endpoint)"
    )
    status: int = Field(..., example=200)
    message: str | None = Field(None, example="Success")
    error: str | None = Field(None, example=None)

class StatVacancyMonthOut(BaseModel):
    data: list[MonthStat] = Field(
        ...,
        description="List of statistic data (depends on endpoint)"
    )
    status: int = Field(..., example=200)
    message: str | None = Field(None, example="Success")
    error: str | None = Field(None, example=None)

class GetUserProfile(BaseModel):
    id: int
    telegram_id: int

class GetUserPost(BaseModel):
    id: int
    vacancy_type: str