from constants import BASE_URL, USER_ENDPOINT
from custom_requester.custom_requester import CustomRequester


class UserAPI(CustomRequester):
    '''
    Класс для работы с API пользователей
    '''

    USER_BASE_URL = BASE_URL

    def __init__(self, session):
        super().__init__(session=session, base_url=self.USER_BASE_URL)

    def get_user(self, user_locator, expected_status=200):
        return self.send_request("GET",
                                 f"{USER_ENDPOINT}/{user_locator}",
                                 expected_status=expected_status
                                 )

    def create_user(self, user_data, expected_status=201):
        return self.send_request(
            method="POST",
            endpoint=USER_ENDPOINT,
            data=user_data,
            expected_status=expected_status
        )

    def delete_user(self, user_id):
        return self.send_request(
            method='DELETE',
            endpoint=f'{USER_ENDPOINT}/{user_id}'
        )