from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy.orm import Session
from project.db_models.movie import MovieDBModel
from project.db_models.user import UserDBModel


class DBHelper:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    """Класс с методами для работы с БД в тестах"""

    def create_test_user(self, user_data: dict) -> UserDBModel:
        """Создает тестового пользователя"""
        user = UserDBModel(**user_data)
        self.db_session.add(user)
        self.db_session.commit()
        self.db_session.refresh(user)
        return user

    def _movie_payload_to_db(self, payload: dict) -> dict:
        """CamelCase (API/генератор) → snake_case (ORM/БД)."""
        return {
            "name": payload["name"],
            "description": payload["description"],
            "genre_id": payload["genreId"],
            "image_url": payload.get("imageUrl"),
            "price": Decimal(str(payload["price"])) if hasattr(MovieDBModel.price.type,
                                                               'asdecimal') else
            payload["price"],
            "rating": payload.get("rating"),
            "location": payload["location"],
            "published": payload["published"],
            "created_at": payload.get("createdAt") or datetime.now(timezone.utc)
        }

    def create_test_movie(self, movie_data: dict) -> MovieDBModel:
        '''Создаем тестовый фильм'''
        data = self._movie_payload_to_db(movie_data)
        movie = MovieDBModel(**data)
        self.db_session.add(movie)
        self.db_session.commit()
        self.db_session.refresh(movie)
        return movie


    def get_user_by_id(self, user_id: str):
        """Получает пользователя по ID"""
        return self.db_session.query(UserDBModel).filter_by(id = user_id).first()

    def get_movie_by_id(self, movie_id: int):
        '''Получает фильм по ID'''
        return self.db_session.query(MovieDBModel).filter_by(id = movie_id).first()

    def get_movie_by_name(self, movie_name: str):
        '''Получаем фильм по названию'''
        return self.db_session.query(MovieDBModel).filter_by(name=movie_name).first()

    def get_user_by_email(self, email: str):
        """Получает пользователя по email"""
        return self.db_session.query(UserDBModel).filter_by(email = email).first()

    def get_movie_by_name(self, name: str):
        """Получает фильм по названию"""
        return self.db_session.query(MovieDBModel).filter_by(name = name).first()

    def user_exists_by_email(self, email: str) -> bool:
        """Проверяет существование пользователя по email"""
        return (self.db_session.query(UserDBModel).filter_by(email = email).first() is
                not None)

    def movie_exists_by_id(self, movie_id: int) -> bool:
        """Проверяет существование фильма по id"""
        return (self.db_session.query(MovieDBModel).filter_by(id=movie_id).first() is
                not None)

    def delete_user(self, user: UserDBModel):
        """Удаляет пользователя"""
        self.db_session.delete(user)
        self.db_session.commit()

    def delete_movie(self, movie: MovieDBModel):
        """Удаляет фильм"""
        self.db_session.delete(movie)
        self.db_session.commit()

    def cleanup_test_data(self, objects_to_delete: list):
        """Очищает тестовые данные"""
        for obj in objects_to_delete:
            if obj:
                self.db_session.delete(obj)
        self.db_session.commit()


'''
Пример хелпера для movies
def get_movie_by_id(self, movie_id: str):
    """Получает фильм по ID"""
    return self.db_session.query(MovieDBModel).filter(MovieDBModel.id == movie_id).first()
'''
