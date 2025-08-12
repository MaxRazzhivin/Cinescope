import copy
import requests
from faker import Faker
from constants import BASE_URL, BOOKING_ENDPOINT

faker = Faker()


def create_booking(requester, booking_data):
    response = requester.send_request(
        method='POST',
        endpoint=BOOKING_ENDPOINT,
        data=booking_data,
        expected_status=200
    )
    assert response.status_code == 200
    response_data = response.json()
    booking_id = response_data.get("bookingid")
    assert booking_id is not None, "Идентификатор брони не найден в ответе"
    return booking_id, response_data["booking"]


class TestBookings:

    # Создаём бронирование
    def test_create_booking(self, requester, booking_data):
        booking_id, booking = create_booking(requester, booking_data)
        assert booking["firstname"] == booking_data["firstname"], \
            "Заданное имя не совпадает"
        assert booking["totalprice"] == booking_data["totalprice"], \
            "Заданная стоимость не совпадает"

    # Проверяем получение и удаление брони
    def test_get_and_delete_booking(self, requester, auth_requester, booking_data):
        booking_id, _ = create_booking(requester, booking_data)

        # GET проверка - не требуется авторизация
        get_booking = requester.send_request(
            method='GET',
            endpoint=f"{BOOKING_ENDPOINT}/{booking_id}",
            expected_status=200
        )
        assert get_booking.status_code == 200, "Бронь не найдена"
        assert get_booking.json()["lastname"] == booking_data['lastname']

        # Удаляем бронирование - требуется авторизация auth_requester
        deleted_booking = auth_requester.send_request(
            method='DELETE',
            endpoint=f"{BOOKING_ENDPOINT}/{booking_id}",
            expected_status=201
        )
        assert deleted_booking.status_code == 201, "Бронь не удалилась"

        # Проверяем, что бронирование больше недоступно
        get_booking = requester.send_request(
            method="GET",
            endpoint=f"{BOOKING_ENDPOINT}/{booking_id}",
            expected_status=404
        )
        assert get_booking.status_code == 404, "Бронь не удалилась"

    def test_refresh_booking(self, auth_requester, requester, booking_data):
        booking_id, _ = create_booking(requester, booking_data)

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

        # Вносим изменения в нашу бронь - метод PUT, нужна авторизация
        renew_booking = auth_requester.send_request(
            method='PUT',
            endpoint=f"{BOOKING_ENDPOINT}/{booking_id}",
            data=updated_data,
            expected_status=200
        )
        assert renew_booking.status_code == 200, "Обновление брони не удалось"

        # Проверяем чо вышло через метод GET
        get_booking = requester.send_request(
            method='GET',
            endpoint=f"{BOOKING_ENDPOINT}/{booking_id}",
            expected_status=200
        )
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

    def test_patch_booking(self, auth_requester, requester, booking_data):
        booking_id, _ = create_booking(requester, booking_data)

        # Создаем новые данные через faker
        patched_data = {
            "firstname": faker.first_name(),
            "additionalneeds": "Girl"
        }

        # Вносим изменения в нашу бронь - PATCH требует авторизации
        patch_booking = auth_requester.send_request(
            method='PATCH',
            endpoint=f"{BOOKING_ENDPOINT}/{booking_id}",
            data=patched_data,
            expected_status=200
        )
        assert patch_booking.status_code == 200, "Обновление брони не удалось"
        assert patch_booking.json()["firstname"] == patched_data["firstname"]
        assert patch_booking.json()["additionalneeds"] == patched_data[
            "additionalneeds"]

        # Получаем через GET и сверяемся с ответом

        get_booking = requester.send_request(
            method='GET',
            endpoint=f"{BOOKING_ENDPOINT}/{booking_id}",
            expected_status=200
        )
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

    def test_post_book_with_missing_fields(self, auth_requester, booking_data):
        # Пропущено поле "firstname"
        invalid_payload = copy.deepcopy(booking_data)
        invalid_payload.pop("firstname")

        response = auth_requester.send_request(
            method='POST',
            endpoint=BOOKING_ENDPOINT,
            data=invalid_payload,
            expected_status=500
        )
        # Проверяем, что вернулся 500 (или, если бы API был адекватным — ожидали бы 400)
        assert response.status_code == 500, ("Ожидали 500 из-за отсутствия "
                                             "обязательного поля")

    def test_post_book_with_error_format_fields(self, auth_requester, booking_data):
        # Формат введем число вместо строки
        invalid_payload = copy.deepcopy(booking_data)
        invalid_payload["firstname"] = 12345

        response = auth_requester.send_request(
            method='POST',
            endpoint=BOOKING_ENDPOINT,
            data=invalid_payload,
            expected_status=500
        )
        # Проверяем, что вернулся 500 (или, если бы API был адекватным — ожидали бы 400)
        assert response.status_code == 500, ("Ожидали 500 из-за отсутствия "
                                             "обязательного поля")

    def test_get_nonexistent_booking(self, requester):
        nonexistent_id = 3089089  # рандомный id, которого нет
        response = requester.send_request(
            method='GET',
            endpoint=f"{BOOKING_ENDPOINT}/{nonexistent_id}",
            expected_status=404
        )
        assert response.status_code == 404, ("ожидаем 404 Not Found при попытке GET "
                                             "несуществующего букинга")

    def test_patch_nonexistent_booking(self, auth_requester):
        nonexistent_id = 3089089  # рандомный id, которого нет
        new_data = {
            "firstname": faker.first_name(),
            "additionalneeds": "Cocktail"
        }
        response = auth_requester.send_request(
            method='PATCH',
            endpoint=f"{BOOKING_ENDPOINT}/{nonexistent_id}",
            data=new_data,
            expected_status=405
        )
        assert response.status_code in (404, 405), (
            f"Ожидали 404 Not Found или 405 Method Not Allowed, но получили "
            f"{response.status_code}")

    def test_delete_without_auth(self, requester, auth_requester, booking_data):
        # Создаём авторизованную бронь через заготовленную сессию
        booking_id, _ = create_booking(requester, booking_data)

        # Создаём неавторизованный сеанс (без токена) и пробуем удалить бронь новую

        response = requester.send_request(
            method='DELETE',
            endpoint=f"{BOOKING_ENDPOINT}/{booking_id}",
            expected_status=403
        )

        # Проверяем, что сервер запретил это действие
        assert response.status_code == 403 or response.status_code == 401, \
            "Ожидали 403/401 при удалении без авторизации"
