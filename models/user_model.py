import datetime
from typing import Optional

from pydantic import BaseModel, Field, EmailStr, field_validator

from constants import Roles


class UserModel(BaseModel):
    email: EmailStr
    fullName: str
    password: str = Field(..., min_length=8, description='Поле для ввода пароля')
    passwordRepeat: str = Field(..., min_length=8, description='Поле для повтора ввода '
                                                               'пароля')
    roles: list[Roles] = [Roles.USER] # внес в модель список юзеров через Enum
    banned: Optional[bool] = None
    verified: Optional[bool] = None

    class Config:
        json_encoders = {
            Roles: lambda v: v.value  # Превращаем Enum -> строку
        }

    # @field_validator('email')
    # def check_email(cls, value: str):
    #     if '@' not in value:
    #         raise ValueError('Email должен содержать знак @')
    #     return value

    @field_validator("passwordRepeat")
    def check_password_repeat(cls, value: str, info) -> str:
        pwd = info.data.get("password")
        if pwd is not None and value != pwd:
            raise ValueError("Пароли не совпадают")
        return value

class RegisterUserResponse(BaseModel):
    id: str
    email: EmailStr
    fullName: str = Field(min_length=1, max_length=100, description="Полное имя пользователя")
    verified: bool = False
    roles: list[Roles]
    createdAt: str = Field(description="Дата и время создания пользователя в формате ISO 8601")

    @field_validator("createdAt")
    def validate_created_at(cls, value: str) -> str:
        # Валидатор для проверки формата даты и времени (ISO 8601).
        try:
            datetime.datetime.fromisoformat(value)
        except ValueError:
            raise ValueError("Некорректный формат даты и времени. Ожидается формат ISO 8601.")
        return value
