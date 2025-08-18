from conftest import api_manager
from constants import LOGIN_ENDPOINT
from tests.api.api_manager import ApiManager


class TestAuthAPI:
    def test_register_user(self, registered_user):
        """
        Тест на регистрацию пользователя.
        """
        response_data, test_user_with_id = registered_user

        # Проверки
        assert response_data["email"] == test_user_with_id["email"], "Email не совпадает"
        assert "id" in response_data, "ID пользователя отсутствует в ответе"
        assert "roles" in response_data, "Роли пользователя отсутствуют в ответе"
        assert "USER" in response_data["roles"], "Роль USER должна быть у пользователя"

    def test_register_and_login_user(self, api_manager: ApiManager, registered_user):
        """
        Тест на регистрацию и авторизацию пользователя.
        """
        _, test_user_with_id = registered_user

        login_data = {
            "email": test_user_with_id["email"],
            "password": test_user_with_id["password"]
        }
        response = api_manager.auth_api.login_user(login_data)
        response_data = response.json()

        # Проверки
        assert "accessToken" in response_data, "Токен доступа отсутствует в ответе"
        assert response_data["user"]["email"] == test_user_with_id["email"], "Email не совпадает"


    def test_login_wrong_password(self, api_manager: ApiManager, registered_user):
        '''
        Тест на авторизацию с неверным паролем
        Задаем статус 401, так как в методе по умолчанию 200 идет
        '''

        _, test_user_with_id = registered_user

        wrong_data = {
            'email': test_user_with_id['email'],
            'password': 'some_error_passwrd123'
        }
        response = api_manager.auth_api.login_user(wrong_data, expected_status=401)

        assert "error" in response.json() or "message" in response.json(), \
            "В ответе нет информации об ошибке"

    def test_login_empty_body(self, api_manager):
        '''
        Тест на авторизацию с пустым телом запроса
        Ошибку ждем 401
        '''

        empty_creds = {
            'email': '',
            'password': ''
        }
        response = api_manager.auth_api.login_user(login_data=empty_creds, expected_status=401)

        assert "error" in response.json() or "message" in response.json(), \
            "В ответе нет информации об ошибке"

