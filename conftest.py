import pytest
import requests
from faker import Faker
from constants import HEADERS, BASE_URL, REGISTER_ENDPOINT, LOGIN_ENDPOINT
from custom_requester.custom_requester import CustomRequester

faker = Faker()


# @pytest.fixture(scope="session")
# def auth_session():
#     # Создаём сессию один раз на все тесты
#     session = requests.Session()
#
#     # Обновляем заголовки в сессии — теперь все запросы через session будут иметь
#     # нужные хэдеры
#     session.headers.update(HEADERS)
#
#     response = session.post(
#         f"{BASE_URL}/auth",
#         json={"username": "admin", "password": "password123"}
#     )
#     assert response.status_code == 200, "Ошибка авторизации"
#     token = response.json().get("token")
#     assert token is not None, "В ответе не оказалось токена"
#
#     # Добавляем токен как cookie в сессию — будет передаваться в каждом последующем
#     # запросе
#     session.cookies.set("token", token)
#     return session


# @pytest.fixture
# def booking_data():
#     return {
#         "firstname": faker.first_name(),
#         "lastname": faker.last_name(),
#         "totalprice": faker.random_int(min=100, max=100000),
#         "depositpaid": True,
#         "bookingdates": {
#             "checkin": "2024-04-05",
#             "checkout": "2024-04-08"
#         },
#         "additionalneeds": "Cigars"
#     }


@pytest.fixture(scope='session')
def booking_data():
    '''
    Генерация случайного букинга для тестов
    '''
    firstname = faker.first_name()
    lastname = faker.last_name()
    totalprice = faker.random_int(min=100, max=100000)
    depositpaid = True
    bookingdates = {
        "checkin": "2024-04-05",
        "checkout": "2024-04-08"
    }
    additionalneeds = "Cigars"

    return {
        "firstname": firstname,
        "lastname": lastname,
        'totalprice': totalprice,
        'depositpaid': depositpaid,
        'bookingdates': bookingdates,
        'additionalneeds': additionalneeds
    }


@pytest.fixture(scope='session')
def requester():
    """
    Фикстура для создания экземпляра CustomRequester.
    Неавторизованный клиент
    """
    session = requests.Session()
    session.headers.update(HEADERS)
    return CustomRequester(session=session, base_url=BASE_URL)


@pytest.fixture(scope='session')
def auth_requester():
    '''
    Авторизованный клиент (cookie token)
    '''

    session = requests.Session()
    session.headers.update(HEADERS)
    r = CustomRequester(session=session, base_url=BASE_URL)

    resp = r.send_request(
        method="POST",
        endpoint=LOGIN_ENDPOINT,
        data={"username": "admin", "password": "password123"},
        expected_status=200
    )

    token = resp.json().get('token')
    assert token is not None, "В ответе /auth нет токена"

    # Restful-booker принимает токен как cookie
    r.session.cookies.set('token', token)
    return r

#
# @pytest.fixture(scope='session')
# def registered_user(requester, test_user):
#     '''
#     Фикстуры для регистрации и получения данных зарегистрированного пользователя
#     '''
#     response = requester.send_request(
#         method='POST',
#         endpoint=REGISTER_ENDPOINT,
#         data=test_user,
#         expected_status=201
#     )
#
#     response_data = response.json()
#     test_user_with_id = test_user.copy()
#     test_user_with_id['id'] = response_data['id']
#     return response_data, test_user_with_id
