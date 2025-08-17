from constants import BASE_URL
from custom_requester.custom_requester import CustomRequester


class UserAPI(CustomRequester):
    '''
    Класс для работы с API пользователей
    '''

    def __init__(self, session):
        super().__init__(session=session, base_url=BASE_URL)

    def get_user_info(self, user_id, expected_status=200):
        '''
        Получение информации о пользователе.
        :param user_id: ID пользователя.
        :param expected_status: Ожидаемый статус-код.
        '''
        return self.send_request(
            method="GET",
            endpoint=f'/users/{user_id}',
            expected_status=expected_status
        )

    def delete_user(self, user_id, expected_status=204):
        '''
        Удаление пользователя.
        :param user_id: ID пользователя.
        :param expected_status: Ожидаемый статус-код.
        '''
        return self.send_request(
            method='DELETE',
            endpoint=f'/users/{user_id}',
            expected_status=expected_status
        )

    def clean_up_user(self, user_id):
        try:
            self.delete_user(user_id, expected_status=204)
        except ValueError:
            # уже удалён или нет прав
            pass