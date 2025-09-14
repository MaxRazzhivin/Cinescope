from datetime import datetime
from pydantic import BaseModel, Field, EmailStr
from constants import Roles

class CreateUserRequest(BaseModel):
    email: EmailStr
    fullName: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=8)
    verified: bool = True
    banned: bool = False
    roles: list[Roles] = [Roles.USER]

class CreateUserResponse(BaseModel):
    id: str
    email: EmailStr
    fullName: str
    roles: list[Roles]
    verified: bool
    banned: bool
    createdAt: datetime

class GetUserResponse(BaseModel):
    id: str
    email: EmailStr
    fullName: str
    roles: list[Roles]
    verified: bool
    banned: bool
    createdAt: datetime


