from pydantic import BaseModel, Field

class CreateIndustry(BaseModel):
    name: str

class IndustryResponse(BaseModel):
    data: dict | list = Field(
        ...,
        description="List of statistic data (depends on endpoint)"
    )
    status: int = Field(..., example=200)
    message: str | None = Field(None, example="Success")
    error: str | None = Field(None, example=None)

class IndustryOut(BaseModel):
    id: int
    name: str