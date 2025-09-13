from tests.api.auth_api import AuthAPI
from tests.api.movies_api import MoviesApi
from tests.api.user_api import UserAPI


class ApiManager:
    '''
    Класс для управления API-классоми с единой HTTP-сессией.
    '''

    def __init__(self, session):
        '''
        Инициализация ApiManager.
        :param session: HTTP-сессия, используемая всеми API-классами.
        '''

        self.session = session
        self.auth_api = AuthAPI(session)
        self.user_api = UserAPI(session)
        self.movies_api = MoviesApi(session)

    def close_session(self):
        self.session.close()