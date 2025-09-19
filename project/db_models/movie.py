from typing import Dict, Any
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Float
from project.db_models import Base

class MovieDBModel(Base):
    __tablename__ = 'movies'

    id = Column(Integer, primary_key=True, autoincrement=True)   # text в БД
    name = Column(String)
    description = Column(String)
    genre_id = Column(Integer)
    image_url = Column(String)
    price = Column(Float)
    rating = Column(Float)
    location = Column(String)
    published = Column(Boolean)
    created_at = Column(DateTime(timezone=True))

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'genreId': self.genre_id,
            'imageUrl': self.image_url,
            'price': self.price,
            'rating': self.rating,
            'location': self.location,
            'published': self.published,
            'createdAt': self.created_at,
            }

    def __repr__(self):
        return f"<Movie(id='{self.id}', name='{self.name}', price={self.price})>"


