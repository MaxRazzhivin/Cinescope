from constants import MOVIES_URL, MOVIES_ENDPOINT
from custom_requester.custom_requester import CustomRequester


class MoviesApi(CustomRequester):
    def __init__(self, session):
        super().__init__(session=session, base_url = MOVIES_URL)

    def get_all_movies(self, expected_status=200):
        '''
        Получение афиш фильмов.
        :param expected_status: Ожидаемый статус-код.
        '''
        return self.send_request(
            method='GET',
            endpoint=MOVIES_ENDPOINT,
            expected_status=expected_status
        )

    def get_movies_with_filter(self, query=None, expected_status=200):
        '''
        Получение фильмов по фильтрам

        Пример query: {
            "minPrice": 100, "maxPrice": 1000,
            "locations": ["MSK", "SPB"],   # requests сам превратит
             в &locations=MSK&locations=SPB
            "genreId": 1,
            "published": True,
            "page": 1, "pageSize": 20
        }
        '''
        return self.send_request(
            method='GET',
            endpoint=MOVIES_ENDPOINT,
            params=query,
            expected_status=expected_status
        )

    def create_movie(self, movie_data, expected_status=201):
        '''
        :param movie_data: Данные о фильме
        :param expected_status: Ожидаемый статус-код
        :return:
        '''
        return self.send_request(
            method='POST',
            endpoint=MOVIES_ENDPOINT,
            data=movie_data,
            expected_status=expected_status
        )

    def get_movie_by_id(self, movie_id, expected_status=200):
        return self.send_request(
            method='GET',
            endpoint=f'{MOVIES_ENDPOINT}/{movie_id}',
            expected_status=expected_status
        )

    def update_movie(self, movie_id, movie_data, expected_status=200):
        return self.send_request(
            method='PATCH',
            endpoint=f'{MOVIES_ENDPOINT}/{movie_id}',
            data=movie_data,
            expected_status=expected_status
        )

    def delete_movie(self, movie_id, expected_status=204):
        return self.send_request(
            method='DELETE',
            endpoint=f'{MOVIES_ENDPOINT}/{movie_id}',
            expected_status=expected_status
        )