import pytest
import requests
from faker import Faker
from constants import HEADERS, BASE_URL

faker = Faker()


@pytest.fixture(scope="session")
def auth_session():
    # Создаём сессию один раз на все тесты
    session = requests.Session()

    # Обновляем заголовки в сессии — теперь все запросы через session будут иметь
    # нужные хэдеры
    session.headers.update(HEADERS)

    response = session.post(
        f"{BASE_URL}/auth",
        json={"username": "admin", "password": "password123"}
    )
    assert response.status_code == 200, "Ошибка авторизации"
    token = response.json().get("token")
    assert token is not None, "В ответе не оказалось токена"

    # Добавляем токен как cookie в сессию — будет передаваться в каждом последующем
    # запросе
    session.cookies.set("token", token)
    return session


@pytest.fixture
def booking_data():
    return {
        "firstname": faker.first_name(),
        "lastname": faker.last_name(),
        "totalprice": faker.random_int(min=100, max=100000),
        "depositpaid": True,
        "bookingdates": {
            "checkin": "2024-04-05",
            "checkout": "2024-04-08"
        },
        "additionalneeds": "Cigars"
    }
