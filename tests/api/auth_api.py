from collections.abc import Mapping
from typing import Union

from pydantic import BaseModel

from constants import REGISTER_ENDPOINT, LOGIN_ENDPOINT, BASE_URL
from custom_requester.custom_requester import CustomRequester
from models.user_model import UserModel, LoginRequest


class AuthAPI(CustomRequester):
    '''
    Класс для работы с аутентификацией
    '''

    def __init__(self, session):
        super().__init__(session=session,
                         base_url=BASE_URL)

    # Метод для валидации между словарем и объектом Pydantic -> возвращает словарь
    def _to_payload(self, data: Union[BaseModel, Mapping]):
        if isinstance(data, BaseModel):
            return data.model_dump(exclude_unset=True)
        return dict(data)

    def register_user(self, user_data:Union[UserModel, dict], expected_status=201):
        '''
        Регистрация нового пользователя.
        :param user_data: Данные пользователя.
        :param expected_status: Ожидаемый статус-код.
        '''
        payload = self._to_payload(user_data) # Отправляем в валидатор, убеждаемся,
        # что будет словарь

        return self.send_request(
            method='POST',
            endpoint=REGISTER_ENDPOINT,
            data=payload,
            expected_status=expected_status
        )

    def login_user(self, login_data: Union[LoginRequest, dict], expected_status=201):
        '''
        Авторизация пользователя.
        :param login_data: Данные для логина.
        :param expected_status: Ожидаемый статус-код.
        '''
        return self.send_request(
            method='POST',
            endpoint=LOGIN_ENDPOINT,
            data=login_data,
            expected_status=expected_status
        )

    def authenticate(self, user_creds):
        login_data = {
            'email': user_creds[0],
            'password': user_creds[1]
        }

        response = self.login_user(login_data).json()
        if 'accessToken' not in response:
            raise KeyError('token is missing')

        token = response['accessToken']
        self.update_session_headers(self.session, Authorization=f"Bearer {token}")
        return token
