from pydantic import BaseModel, Field

class JobVacancyForm(BaseModel):
    country_id: int = Field(None, description="Ma'mleket")
    region_id: int | None = Field(None, description="Region")
    position_title: str = Field(None, description="Lawazım") # Lawazım
    organization_name: str | None = Field(None, description="Mekeme") # Mekeme
    address: str = Field(None, description="Mánzil hám format") # Mánzil
    requirements: str = Field(None, description="Talaplar") # Talaplar
    duties: str | None = Field(None, description="Májburiyatlar") # Májburiyatlar
    work_schedule: str = Field(None, description="Jumıs waqıtı/formatı:") # Jumıs waqıtı/formatı:
    salary: str = Field(None, description="Aylıq") # Aylıq
    contact: str = Field(None, description="Baylanıs") # Baylanıs
    additional_info: str | None = Field(None, description="Qosımsha") # Qosımsha

class CreateInternship(BaseModel):
    country_id: int = Field(None, description="Ma'mleket")
    region_id: int | None = Field(None, description="Region")
    position_title: str = Field(None, description="Lawazım") # Lawazım
    organization_name: str | None = Field(None, description="Mekeme") # Mekeme
    requirements: str = Field(None, description="Talaplar") # Talaplar
    duties: str | None = Field(None, description="Májburiyatlar") # Májburiyatlar
    conditions: str = Field(None, description="Shárayatlar") # Shárayatlar
    address: str = Field(None, description="Mánzil hám format") # Mánzil hám format
    salary: str = Field(None, description="Aylıq") # Aylıq
    contact: str = Field(None, description="Baylanıs") # Baylanıs
    additional_info: str | None = Field(None, description="Qosımsha") # Qosımsha

class CreateOneTimeTask(BaseModel):
    country_id: int = Field(None, description="Ma'mleket")
    region_id: int | None = Field(None, description="Region")
    who_needed: str = Field(None, description="Sizge kim kerek?")
    task_description: str = Field(None, description="Ne islew kerek?")
    deadline: str | None = Field(None, description="Tamam boliw waqiti")
    salary: str = Field(None, description="Aylıq") # Aylıq
    contact: str = Field(None, description="Baylanıs") # Baylanıs
    address: str | None = Field(None, description="Mánzil hám format") # Mánzil hám format
    additional_info: str | None = Field(None, description="Qosımsha")

class ApproveVacancyForm(BaseModel):
    vacancy_id: int
    vacancy_type: str = Field(None, description="job | internship | one-time-task | opportunities_grants")