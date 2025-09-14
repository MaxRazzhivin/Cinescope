from datetime import datetime
from enum import Enum
from typing import Optional, List

from pydantic import BaseModel, Field


class Location(str, Enum):
    MSK = 'MSK'
    SPB = 'SPB'

class Genre(BaseModel):
    name: str

class MoviesResponse(BaseModel):
    id: int
    name: str
    description: str
    genreId: int
    imageUrl: Optional[str] = None
    price: int
    rating: int
    location: Location
    published: bool
    createdAt: datetime
    genre: Genre


class GetMovies(BaseModel):
    movies: List[MoviesResponse]
    count: int
    page: int
    pageSize: int
    pageCount: int


class MoviesFilter(BaseModel):
    minPrice: Optional[int] = None
    maxPrice: Optional[int] = None
    locations: Optional[list[Location]] = None
    genreId: Optional[int] = None
    published: Optional[bool] = None
    page: Optional[int] = None
    pageSize: Optional[int] = None

class PostMovieRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    imageUrl: Optional[str] = None
    price: int = Field(gt=0)
    description: str = Field(..., min_length=1)
    location: Location
    published: bool
    genreId: int

class PatchMovieRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    genreId: Optional[str] = None
    imageUrl: Optional[str] = None
    price: Optional[int] = None
    rating: Optional[str] = None