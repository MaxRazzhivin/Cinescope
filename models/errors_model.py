from typing import Literal, List
from pydantic import BaseModel

class ForbiddenResponse(BaseModel):
    message: str
    error: Literal["Forbidden"]
    statusCode: Literal[403]

class UnauthorizedResponse(BaseModel):
    message: Literal["Unauthorized"]
    statusCode: Literal[401]


class BadRequestResponse(BaseModel):
    message: List[str]
    error: Literal["Bad Request"]
    statusCode: Literal[400]

class CinemaNotFound(BaseModel):
    message: str
    error: Literal['Not Found']
    statusCode: Literal[404]

class Conflict(BaseModel):
    message: str
    error: Literal['Conflict']
    statusCode: Literal[409]