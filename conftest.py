import time
from typing import Iterator

import pytest
import requests
from sqlalchemy.orm import Session

from constants import Roles
from entities.user import User
from models.movies_model import PostMovieRequest
from models.user_create_models import CreateUserRequest
from models.user_model import UserModel, RegisterUserResponse
from project.db_requester.db_client import get_db_session
from project.db_requester.db_helpers import DBHelper
from resources.user_creds import SuperAdminCreds
from tests.api.api_manager import ApiManager
from utils.data_generator import DataGenerator

@pytest.fixture
def test_user() -> UserModel:
    '''
    Генерация случайного пользователя для тестов через модель Pydantic
    Наружу возвращаем объект модели UserModel для чистоты, десериализация будет позже
    ближе к API передаче данных
    '''
    random_email = DataGenerator.generate_random_email()
    random_name = DataGenerator.generate_random_name()
    random_password = DataGenerator.generate_random_password()

    return UserModel(
        email=random_email,
        fullName=random_name,
        password=random_password,
        passwordRepeat=random_password,
        roles=[Roles.USER]
    )

@pytest.fixture
def registered_user(super_admin, test_user):
    '''
    Фикстуры для регистрации и получения данных зарегистрированного пользователя
    '''

    # Здесь сам запрос и сверка статус-кода ответа
    response = super_admin.api.auth_api.register_user(test_user)
    assert response.status_code == 201

    # Здесь валидация ответа через Pydantic, внутри распаковка словаря для создания
    # объекта от класса RegisterUserResponse
    response_data_model = RegisterUserResponse(**response.json())

    # создаем копию юзера, в который далее положим id для удобства
    test_user_with_id = test_user.model_dump().copy()

    # добавляем в него id из сообщения об успешной регистрации
    test_user_with_id['id'] = response_data_model.id

    # возвращаем из фикстуры дальше тело ответа и payload изначальный + id в нем
    return response_data_model, test_user_with_id

@pytest.fixture
def test_movie():
    return PostMovieRequest(**DataGenerator.generate_movie_data())

@pytest.fixture
def created_movie(super_admin, test_movie):
    response = super_admin.api.movies_api.create_movie(test_movie,
                                                   expected_status=201)
    response_body = response.json()
    yield response_body, test_movie

    # teardown
    try:
        super_admin.api.movies_api.delete_movie(response_body['id'], expected_status=200)
    except Exception:
        pass


@pytest.fixture
def user_session():
    user_pool = []

    def _create_user_session():
        session = requests.Session()
        user_session = ApiManager(session)
        user_pool.append(user_session)
        return user_session

    yield _create_user_session

    for user in user_pool:
        user.close_session()


@pytest.fixture
def super_admin(user_session):
    new_session = user_session()

    super_admin = User(
        SuperAdminCreds.SUPER_ADMIN_USERNAME,
        SuperAdminCreds.SUPER_ADMIN_PASSWORD,
        [Roles.SUPER_ADMIN],
        new_session
    )

    super_admin.api.auth_api.authenticate(super_admin.creds)
    return super_admin

@pytest.fixture
def common_user(user_session, super_admin, creation_user_data: CreateUserRequest):
    new_session = user_session()

    new_user = super_admin.api.user_api.create_user(creation_user_data,
                                                    expected_status=201)
    new_user_id = new_user.json()['id']

    common_user = User(
        creation_user_data.email,
        creation_user_data.password,
        [Roles.USER],
        new_session)


    common_user.api.auth_api.authenticate(common_user.creds)
    yield common_user

    try:
        super_admin.api.user_api.delete_user(new_user_id)
    except Exception:
        pass

@pytest.fixture
def admin_user(user_session, super_admin, creation_user_data):
    new_session = user_session()

    payload = creation_user_data.model_dump().copy()
    payload['roles'] = [Roles.ADMIN.value]

    new_admin = super_admin.api.user_api.create_user(payload, expected_status=201)
    new_admin_id = new_admin.json()['id']

    admin_user = User(
        payload['email'],
        payload['password'],
        [Roles.ADMIN],
        new_session
    )

    admin_user.api.auth_api.authenticate(admin_user.creds)
    yield admin_user

    try:
        super_admin.api.user_api.delete_user(new_admin_id)
    except Exception:
        pass




@pytest.fixture
def creation_user_data(test_user: UserModel) -> CreateUserRequest:
    updated_data = test_user.model_dump().copy()
    updated_data.update({
        'verified': True,
        'banned': False
    })
    return CreateUserRequest(**updated_data)

@pytest.fixture
def created_user(super_admin, creation_user_data):

    user = super_admin.api.user_api.create_user(creation_user_data,
                                                 expected_status=201).json()
    yield user, creation_user_data

    # teardown
    try:
        super_admin.api.user_api.delete_user(user["id"])
    except Exception:
        pass


@pytest.fixture(scope="module")
def db_session() -> Iterator[Session]:
    """
    Фикстура, которая создает и возвращает сессию для работы с базой данных
    После завершения теста сессия автоматически закрывается
    """
    db_session = get_db_session()
    try:
        yield db_session
    finally:
        db_session.close()

@pytest.fixture(scope="function")
def db_helper(db_session) -> DBHelper:
    """
    Фикстура для экземпляра хелпера
    """
    db_helper = DBHelper(db_session)
    return db_helper

@pytest.fixture(scope="function")
def created_test_user(db_helper):
    """
    Фикстура, которая создает тестового пользователя в БД
    и удаляет его после завершения теста
    """
    user = db_helper.create_test_user(DataGenerator.generate_user_data())
    try:
        yield user
    finally:
        # Cleanup после теста
        if db_helper.get_user_by_id(user.id):
            db_helper.delete_user(user)

@pytest.fixture(scope="function")
def created_test_movie(db_helper):
    """
    Фикстура, которая создает тестовый фильм в БД
    и удаляет его после завершения теста
    """
    movie = db_helper.create_test_movie(DataGenerator.generate_movie_data())
    try:
        yield movie
    finally:
        # Cleanup после теста
        if db_helper.get_movie_by_id(movie.id):
            db_helper.delete_movie(movie)

@pytest.fixture
def delay_between_retries():
    time.sleep(5)
    yield
