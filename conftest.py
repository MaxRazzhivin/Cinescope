import pytest
import requests
import os

from dotenv import load_dotenv

from constants import Roles
from entities.user import User
from models.user_model import UserModel
from resources.user_creds import SuperAdminCreds
from tests.api.api_manager import ApiManager
from utils.data_generator import DataGenerator

@pytest.fixture
def test_user():
    '''
    Генерация случайного пользователя для тестов через модель Pydantic
    Наружу возвращаем dict для requests через .model_dump()
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
    ).model_dump(exclude_unset=True)

@pytest.fixture
def registered_user(super_admin, test_user):
    '''
    Фикстуры для регистрации и получения данных зарегистрированного пользователя
    '''
    response = super_admin.api.auth_api.register_user(test_user)

    response_data = response.json()
    test_user_with_id = test_user.copy()
    test_user_with_id['id'] = response_data['id']
    return response_data, test_user_with_id

@pytest.fixture
def test_movie():
    return DataGenerator.generate_movie_data()

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
def common_user(user_session, super_admin, creation_user_data):
    new_session = user_session()

    new_user = super_admin.api.user_api.create_user(creation_user_data)

    common_user = User(
        creation_user_data['email'],
        creation_user_data['password'],
        [Roles.USER],
        new_session)


    common_user.api.auth_api.authenticate(common_user.creds)
    yield common_user

    try:
        super_admin.api.user_api.delete_user(new_user['id'])
    except Exception:
        pass

@pytest.fixture
def admin_user(user_session, super_admin, creation_user_data):
    new_session = user_session()

    payload = creation_user_data.copy()
    payload['roles'] = [Roles.ADMIN.value]

    new_admin = super_admin.api.user_api.create_user(payload)

    admin_user = User(
        payload['email'],
        payload['password'],
        [Roles.ADMIN],
        new_session
    )

    admin_user.api.auth_api.authenticate(admin_user.creds)
    yield admin_user

    try:
        super_admin.api.user_api.delete_user(new_admin['id'])
    except Exception:
        pass




@pytest.fixture
def creation_user_data(test_user):
    updated_data = test_user.copy()
    updated_data.update({
        'verified': True,
        'banned': False,
        "roles": [Roles.USER.value]
    })
    return updated_data

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
