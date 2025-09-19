import random
from datetime import datetime, timezone
from project.db_models.movie import MovieDBModel
from project.db_models.user import UserDBModel
from project.db_requester.db_client import get_db_session
from utils.data_generator import DataGenerator

session = get_db_session()

# Создаем юзера

user = UserDBModel(
    email=DataGenerator.generate_random_email(),
    full_name=DataGenerator.generate_random_name(),
    password=DataGenerator.generate_random_password(),
    created_at=datetime.now(timezone.utc),
    updated_at=datetime.now(timezone.utc),
    verified=False,
    banned=False
)
session.add(user)
session.commit()

found = session.query(UserDBModel).filter(UserDBModel.email==user.email).first()

# Создаем фильм

data = DataGenerator.generate_movie_data()

movie = MovieDBModel(
    name=data['name'],
    description=data['description'],
    genre_id=data['genreId'],
    price=data['price'],
    location=data['location'],
    published=data['published'],
    created_at=datetime.now(timezone.utc),
    rating=random.randint(1,5)
)
session.add(movie)
session.commit()

found_movie = session.query(MovieDBModel).filter(MovieDBModel.name==movie.name).first()


