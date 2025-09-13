from constants import Roles


class TestAuthAPI:
    def test_register_user(self, registered_user):
        """
        Тест на регистрацию пользователя.
        """
        response_data_model, test_user_with_id = registered_user

        # Проверки
        assert response_data_model.fullName == test_user_with_id["fullName"], \
            'Фамилия не совпала в payload и в ответе'

        assert response_data_model.email == test_user_with_id["email"], ("Email не "
                                                                       "совпадает")
        assert Roles.USER in response_data_model.roles, ("Роль USER должна быть у "
                                                    "пользователя")
        # сравнение поля Enum Roles в модели и в JSON-ответе
        assert [r.value for r in response_data_model.roles] == test_user_with_id[
            'roles']

    def test_register_and_login_user(self, registered_user, user_session):
        """
        Тест на регистрацию и авторизацию пользователя.
        """
        _, test_user_with_id = registered_user

        login_data = {
            "email": test_user_with_id["email"],
            "password": test_user_with_id["password"]
        }

        api = user_session()
        response = api.auth_api.login_user(login_data)
        response_data = response.json()

        # Проверки
        assert "accessToken" in response_data, "Токен доступа отсутствует в ответе"
        assert response_data["user"]["email"] == test_user_with_id["email"], "Email не совпадает"


    def test_login_wrong_password(self, registered_user, user_session):
        '''
        Тест на авторизацию с неверным паролем
        Задаем статус 401, так как в методе по умолчанию 200 идет
        '''

        _, test_user_with_id = registered_user

        wrong_data = {
            'email': test_user_with_id['email'],
            'password': 'some_error_passwrd123'
        }

        api = user_session()

        response = api.auth_api.login_user(wrong_data, expected_status=401)

        assert "error" in response.json() or "message" in response.json(), \
            "В ответе нет информации об ошибке"

    def test_login_empty_body(self, user_session):
        '''
        Тест на авторизацию с пустым телом запроса
        Ошибку ждем 401
        '''

        empty_creds = {
            'email': '',
            'password': ''
        }

        api = user_session()

        response = api.auth_api.login_user(login_data=empty_creds, expected_status=401)

        assert "error" in response.json() or "message" in response.json(), \
            "В ответе нет информации об ошибке"

