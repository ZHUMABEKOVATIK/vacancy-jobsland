from pydantic import BaseModel, Field
from src.schemas.locations import LocationOut
from src.schemas.industry import IndustryOut

class TelegramWebAppAuthIn(BaseModel):
    init_data: str = Field(..., description="Telegram WebApp initData string")

class TokenPairOut(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class CreateAccountForm(BaseModel):
    bot_id: int
    user_id: int
    language_code: str

class UpdateProfile(BaseModel):
    language_code: str | None
    full_name: str | None
    contact: str | None
    company_name: str | None
    country_id: int | None
    region_id: int | None
    industry_id: int | None

class IsAuthUser(BaseModel):
    bot_id: int
    user_id: int

class UpdateUserLanguage(BaseModel):
    bot_id: int
    user_id: int
    code: str


class UserProfileOut(BaseModel):
    full_name: str | None
    language: str | None
    company_name: str | None
    location: LocationOut
    contact: str
    telegram_id: int
    industry: IndustryOut | None

class GeneralProfileOut(BaseModel):
    data: UserProfileOut | dict
    status: int
    message: str | None
    error: str | None

class AdminAuth(BaseModel):
    username: str = Field(..., description="Admin username")
    password: str = Field(..., description="Admin password")