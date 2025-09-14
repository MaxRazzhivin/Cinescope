from datetime import datetime, timezone
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
            datetime.fromisoformat(value)
        except ValueError:
            raise ValueError("Некорректный формат даты и времени. Ожидается формат ISO 8601.")
        return value

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, description='Поле для ввода пароля')

class LoginUser(BaseModel):
    id: str
    email: EmailStr
    fullName: str = Field(min_length=1,
                          max_length=100,
                          description="Полное имя пользователя")
    roles: list[Roles]

class LoginResponse(BaseModel):
    user: LoginUser
    accessToken: str
    refreshToken: str
    expiresIn: datetime = Field(description='Дата в формате timestamp в милисекундах')

    # Переводим время в милисекундах в формат ISO 8601 и проверяем на корректность
    @field_validator('expiresIn', mode='before')
    def _convert_field_expires_in(cls, value):
        if isinstance(value, (int, float)):
            token_date_will_expire = datetime.fromtimestamp(value / 1000,
                                                            tz=timezone.utc)
        elif isinstance(value, datetime):
            token_date_will_expire = value
        else:
            raise ValueError('Некорректный формат expiresIn')

        # Проверяем что дата позже нашей текущей
        if token_date_will_expire <= datetime.now(timezone.utc):
            raise ValueError(f'Токен уже истек: {token_date_will_expire.isoformat()}')

        return token_date_will_expire

