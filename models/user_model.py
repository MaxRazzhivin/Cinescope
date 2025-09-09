from pydantic import BaseModel


class UserModel(BaseModel):
    email: str
    fullName: str
    password: str
    passwordRepeat: str
    roles: list[str]