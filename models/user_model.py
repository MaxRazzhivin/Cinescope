from typing import Optional

from pydantic import BaseModel, Field, EmailStr, field_validator

from constants import Roles


class UserModel(BaseModel):
    email: str
    fullName: str
    password: str = Field(..., min_length=8, description='Поле для ввода пароля')
    passwordRepeat: str = Field(..., min_length=8, description='Поле для повтора ввода '
                                                               'пароля')
    roles: list[Roles] # внес в модель список юзеров через Enum
    banned: Optional[bool] = None
    verified: Optional[bool] = None

    @field_validator('email')
    def check_email(cls, value: str):
        if '@' not in value:
            raise ValueError('Email должен содержать знак @')
        return value