import copy

import requests
from faker import Faker

from constants import BASE_URL

faker = Faker()


def create_booking(auth_session, booking_data):
    response = auth_session.post(f"{BASE_URL}/booking", json=booking_data)
    assert response.status_code == 200
    response_json = response.json()
    booking_id = response_json.get("bookingid")
    assert booking_id is not None, "Идентификатор брони не найден в ответе"
    return booking_id, response_json["booking"]


class TestBookings:

    # Создаём бронирование
    def test_create_booking(self, auth_session, booking_data):
        booking_id, booking = create_booking(auth_session, booking_data)
        assert booking["firstname"] == booking_data["firstname"], \
            "Заданное имя не совпадает"
        assert booking["totalprice"] == booking_data["totalprice"], \
            "Заданная стоимость не совпадает"

    # Проверяем получение и удаление брони
    def test_get_and_delete_booking(self, auth_session, booking_data):
        booking_id, _ = create_booking(auth_session, booking_data)

        # GET проверка
        get_booking = auth_session.get(f'{BASE_URL}/booking/{booking_id}')
        assert get_booking.status_code == 200, "Бронь не найдена"
        assert get_booking.json()["lastname"] == booking_data['lastname']

        # Удаляем бронирование
        deleted_booking = auth_session.delete(f"{BASE_URL}/booking/{booking_id}")
        assert deleted_booking.status_code == 201, "Бронь не удалилась"

        # Проверяем, что бронирование больше недоступно
        get_booking = auth_session.get(f"{BASE_URL}/booking/{booking_id}")
        assert get_booking.status_code == 404, "Бронь не удалилась"

    def test_refresh_booking(self, auth_session, booking_data):
        booking_id, _ = create_booking(auth_session, booking_data)

        # Создаем новые данные через faker
        updated_data = {
            "firstname": faker.first_name(),
            "lastname": faker.last_name(),
            "totalprice": faker.random_int(min=100, max=100000),
            "depositpaid": False,
            "bookingdates": {
                "checkin": "2025-01-01",
                "checkout": "2025-01-10"
            },
            "additionalneeds": "Champagne"
        }

        # Вносим изменения в нашу бронь
        renew_booking = auth_session.put(f"{BASE_URL}/booking/{booking_id}",
                                         json=updated_data)
        assert renew_booking.status_code == 200, "Обновление брони не удалось"

        # Проверяем чо вышло
        get_booking = auth_session.get(f"{BASE_URL}/booking/{booking_id}")
        assert get_booking.status_code == 200, "Не удалось получить обновлённую бронь"

        data = get_booking.json()
        assert data["firstname"] == updated_data["firstname"]
        assert data["lastname"] == updated_data["lastname"]
        assert data["totalprice"] == updated_data["totalprice"]
        assert data["depositpaid"] == updated_data["depositpaid"]
        assert data["bookingdates"]["checkin"] == updated_data["bookingdates"][
            "checkin"]
        assert data["bookingdates"]["checkout"] == updated_data["bookingdates"][
            "checkout"]
        assert data["additionalneeds"] == updated_data["additionalneeds"]

    def test_patch_booking(self, auth_session, booking_data):
        booking_id, _ = create_booking(auth_session, booking_data)

        # Создаем новые данные через faker
        patched_data = {
            "firstname": faker.first_name(),
            "additionalneeds": "Girl"
        }

        # Вносим изменения в нашу бронь
        patch_booking = auth_session.patch(f"{BASE_URL}/booking/{booking_id}",
                                           json=patched_data)
        assert patch_booking.status_code == 200, "Обновление брони не удалось"
        assert patch_booking.json()["firstname"] == patched_data["firstname"]
        assert patch_booking.json()["additionalneeds"] == patched_data[
            "additionalneeds"]

        # Получаем через GET и сверяемся с ответом

        get_booking = auth_session.get(f"{BASE_URL}/booking/{booking_id}")
        assert get_booking.status_code == 200, "Не удалось получить обновлённую бронь"

        data = get_booking.json()
        assert data["firstname"] == patched_data["firstname"]
        assert data["lastname"] == booking_data["lastname"]
        assert data["totalprice"] == booking_data["totalprice"]
        assert data["depositpaid"] == booking_data["depositpaid"]
        assert data["bookingdates"]["checkin"] == booking_data["bookingdates"][
            "checkin"]
        assert data["bookingdates"]["checkout"] == booking_data["bookingdates"][
            "checkout"]
        assert data["additionalneeds"] == patched_data["additionalneeds"]


class TestNegativeBooking:

    def test_post_book_with_missing_fields(self, auth_session, booking_data):
        # Пропущено поле "firstname"
        invalid_payload = copy.deepcopy(booking_data)
        invalid_payload.pop("firstname")

        response = auth_session.post(f"{BASE_URL}/booking",
                                     json=invalid_payload)
        # Проверяем, что вернулся 500 (или, если бы API был адекватным — ожидали бы 400)
        assert response.status_code == 500, ("Ожидали 500 из-за отсутствия "
                                             "обязательного поля")
        print("Response text:", response.text)

    def test_post_book_with_error_format_fields(self, auth_session, booking_data):
        # Формат введем число вместо строки
        invalid_payload = copy.deepcopy(booking_data)
        invalid_payload["firstname"] = 12345

        response = auth_session.post(f"{BASE_URL}/booking",
                                     json=invalid_payload)
        # Проверяем, что вернулся 500 (или, если бы API был адекватным — ожидали бы 400)
        assert response.status_code == 500, ("Ожидали 500 из-за отсутствия "
                                             "обязательного поля")
        print("Response text:", response.text)

    def test_get_nonexistent_booking(self, auth_session):
        nonexistent_id = 3089089  # рандомный id, которого нет
        response = auth_session.get(f"{BASE_URL}/booking/{nonexistent_id}")
        assert response.status_code == 404, ("ожидаем 404 Not Found при попытке GET "
                                             "несуществующего букинга")
        print("Response text:", response.text)

    def test_patch_nonexistent_booking(self, auth_session):
        nonexistent_id = 3089089  # рандомный id, которого нет
        new_data = {
            "firstname": faker.first_name(),
            "additionalneeds": "Cocktail"
        }
        response = auth_session.patch(f"{BASE_URL}/booking/{nonexistent_id}",
                                      json=new_data)
        assert response.status_code in (404, 405), (
            f"Ожидали 404 Not Found или 405 Method Not Allowed, но получили "
            f"{response.status_code}")

        print("Response text:", response.text)

    def test_delete_without_auth(self, auth_session, booking_data):
        # Создаём авторизованную бронь через заготовленную сессию
        booking_id, _ = create_booking(auth_session, booking_data)

        # Создаём неавторизованный сеанс (без токена) и пробуем удалить бронь новую
        unauth_session = requests.Session()
        response = unauth_session.delete(f"{BASE_URL}/booking/{booking_id}")

        # Проверяем, что сервер запретил это действие
        assert response.status_code == 403 or response.status_code == 401, \
            "Ожидали 403/401 при удалении без авторизации"
