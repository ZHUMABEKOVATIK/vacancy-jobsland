from pydantic import BaseModel, Field

class CreateChennel(BaseModel):
    country_id: int
    region_id: int | None = None
    channel_url: str

class UpdateChennel(BaseModel):
    country_id: int | None = None
    region_id: int | None = None
    channel_url: str | None = None