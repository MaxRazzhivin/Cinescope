import pytest
import requests
import os

from dotenv import load_dotenv

from constants import BASE_URL, HEADERS, LOGIN_ENDPOINT, MOVIES_URL, MOVIES_ENDPOINT, \
    REGISTER_ENDPOINT
from tests.api.api_manager import ApiManager
from utils.data_generator import DataGenerator

from custom_requester.custom_requester import CustomRequester

load_dotenv()
username = os.getenv('USERNAME')
password = os.getenv('PASSWORD')

# Здесь до рефакторинга авторизация как админ была более длинная

# @pytest.fixture(scope="session")
# def auth_session_admin():
#     # 1. Создаем словарь с данными для авторизации как админ
#     login_data = {
#         "email": username,
#         "password": password
#     }
#     # 2. Авторизация с правами админа
#     response = requests.post(f'{BASE_URL}{LOGIN_ENDPOINT}', json=login_data, headers=HEADERS)
#     assert response.status_code in (200, 201), ("Код ответа для авторизации отличается "
#                                                "от 200 или 201")
#
#     token = response.json().get("accessToken")
#     assert response.json()['user']['email'] == username
#     assert "accessToken" in response.json(), "В ответе нет токена"
#
#     # 3. Создаем отдельную копию заголовков, куда поместим токен
#     auth_headers = HEADERS.copy()
#     auth_headers["Authorization"] = f"Bearer {token}"
#
#     # 4. Создаем сессию
#     session = requests.Session()
#     session.headers.update(auth_headers)
#
#     return session

# @pytest.fixture(scope="module")
# def create_movie(admin_auth):
#     payload = DataGenerator.generate_movie_data()
#
#     response = requests.post(f"{MOVIES_URL}{MOVIES_ENDPOINT}", json=payload)
#     assert response.status_code in (200, 201), "Фильм не удалось создать"
#
#     response_data = response.json()
#
#     yield payload, response_data

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
def auth_session(test_user):
    # Регистрируем нового пользователя
    register_url = f'{BASE_URL}{REGISTER_ENDPOINT}'
    reg_response = requests.post(register_url, json=test_user, headers=HEADERS)

    assert reg_response.status_code in (200, 201),(
        f"Ошибка регистрации: {reg_response.status_code} {reg_response.text}")

    # Логинимся для получения токена
    login_url = f"{BASE_URL}{LOGIN_ENDPOINT}"
    login_data = {
        "email": test_user['email'],
        "password": test_user['password']
    }

    log_response = requests.post(login_url, json=login_data, headers=HEADERS)
    assert log_response.status_code == 200, (
        f"Ошибка авторизации: {log_response.status_code}{log_response.text}")
    log_json = log_response.json()


    # Получаем токен
    token = log_json.get('accessToken')
    assert token is not None, "Токен не найден в ответе"

    # Cоздаем отдельные заголовки с токеном
    auth_headers = HEADERS.copy()
    auth_headers["Authorization"] = f"Bearer {token}"

    # Создаем новую сессию с заголовками
    session = requests.Session()
    session.headers.update(auth_headers)

    return session, reg_response, log_response


@pytest.fixture(scope='session')
def requester():
    """
        Фикстура для создания экземпляра CustomRequester.
        """
    session = requests.Session()
    return CustomRequester(session=session, base_url=BASE_URL)


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




