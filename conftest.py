import pytest
import requests
import os

from dotenv import load_dotenv

from tests.api.api_manager import ApiManager
from utils.data_generator import DataGenerator
load_dotenv()
username = os.getenv('USERNAME')
password = os.getenv('PASSWORD')

@pytest.fixture(scope='session')
def test_user():
    '''
    Генерация случайного пользователя для тестов
    '''
    random_email = DataGenerator.generate_random_email()
    random_name = DataGenerator.generate_random_name()
    random_password = DataGenerator.generate_random_password()

    return {
        "email": random_email,
        "fullName": random_name,
        'password': random_password,
        'passwordRepeat': random_password
    }

@pytest.fixture(scope='session')
def registered_user(api_manager, test_user):
    '''
    Фикстуры для регистрации и получения данных зарегистрированного пользователя
    '''
    response = api_manager.auth_api.register_user(test_user)

    response_data = response.json()
    test_user_with_id = test_user.copy()
    test_user_with_id['id'] = response_data['id']
    return response_data, test_user_with_id


@pytest.fixture(scope='session')
def session():
    '''
    Фикстура для создания HTTP-сессии.
    '''
    http_session = requests.Session()
    yield http_session
    http_session.close()

@pytest.fixture(scope='session')
def api_manager(session):
    '''
    Фикстура для создания экземпляра ApiManager.
    '''
    return ApiManager(session)

@pytest.fixture(scope="session")
def admin_auth(api_manager):
    """
    Автоматическая авторизация админом перед всеми тестами.
    """
    api_manager.auth_api.authenticate((username, password))

@pytest.fixture(scope='session')
def test_movie():
    return DataGenerator.generate_movie_data()

@pytest.fixture
def created_movie(api_manager, test_movie):
    response = api_manager.movies_api.create_movie(test_movie,
                                                   expected_status=201)
    response_body = response.json()
    yield response_body, test_movie

    # teardown
    try:
        api_manager.movies_api.delete_movie(response_body['id'], expected_status=200)
    except Exception:
        pass
