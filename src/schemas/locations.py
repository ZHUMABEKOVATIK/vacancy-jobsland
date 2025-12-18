from pydantic import BaseModel

class ActiveCountry(BaseModel):
    activate: bool

class CreateCountry(BaseModel):
    name: str
    active: bool

class CreateRegion(BaseModel):
    country_id: int
    name: str
    active: bool

class CountryOut(BaseModel):
    id: int
    name: str

class LocationOut(BaseModel):
    country: CountryOut
    region: CountryOut | None