from fastapi_users import schemas
from pydantic import BaseModel, EmailStr


class UserExistTelegram(BaseModel):
    telegram_id: int


class UserRead(schemas.BaseUser[int]):
    id: int
    email: str


class UserCreate(schemas.BaseUserCreate):
    email: EmailStr
    password: str


class UserUpdate(schemas.BaseUserUpdate):
    email: EmailStr
    telegram_id: int

