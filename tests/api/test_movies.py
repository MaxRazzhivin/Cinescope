import json
import os
import random

import requests
from jsonschema import validate

from constants import MOVIES_URL, MOVIES_ENDPOINT, HEADERS
from utils.data_generator import DataGenerator


class TestMoviesAPI:
    def test_get_movies(self, api_manager):
        """
        Тест на получение списка фильмов
        """
        response = api_manager.movies_api.get_all_movies(expected_status=200)
        body=response.json()

        assert isinstance(body['movies'], list), 'Ответ должен быть списком'

        assert 'id' in body['movies'][0], "у фильма должен быть id"
        assert 'name' in body['movies'][0], 'у фильма должно быть название'

        # Валидация ответа от сервера
        schema_path = os.path.join(os.path.dirname(__file__),
                                   "../..",
                                   'schemas',
                                   'get_movies.json')
        with open(schema_path) as file:
            schema = json.load(file)
        validate(response.json(), schema)  # Валидация ответа от сервера


    def test_create_movie(self, created_movie, admin_auth):
        '''
        Тест на создание нового фильма
        '''
        movie, payload = created_movie
        assert movie['name'] == payload['name']
        assert 'id' in movie

        # Валидация ответа от сервера
        schema_path = os.path.join(os.path.dirname(__file__),
                                   "../..",
                                   'schemas',
                                   'post_movie.json')
        with open(schema_path) as file:
            schema = json.load(file)
        validate(movie, schema)  # Валидация ответа от сервера


    def test_get_movie_by_id(self, api_manager, created_movie, admin_auth):
        '''
        Получение инфы про созданный фильм по ID
        '''

        movie, _ = created_movie
        movie_id = movie['id']
        response = api_manager.movies_api.get_movie_by_id(movie_id, expected_status=200)
        assert response.json()['id'] == movie['id']
        assert response.json()['name'] == movie['name']
        assert response.json()['description'] == movie['description']

        # Валидация ответа от сервера
        schema_path = os.path.join(os.path.dirname(__file__),
                                   "../..",
                                   'schemas',
                                   'get_new_movie_by_id.json')
        with open(schema_path) as file:
            schema = json.load(file)
        validate(response.json(), schema)  # Валидация ответа от сервера


    def test_update_movie(self, api_manager, admin_auth, created_movie):
        '''
        Обновление инфы о фильме через метод PATCH
        '''
        movie, payload = created_movie
        movie_id = movie['id']

        updated_movie_payload = {
            'name': payload['name'] + ' Updated',
            'description': payload['description'] + ' Something new for update',
            'price': payload['price'] + random.randint(100,500)
        }

        response = api_manager.movies_api.update_movie(movie_id,
                                                       movie_data=updated_movie_payload,
                                                       expected_status=200)

        assert response.status_code == 200, "Обновление инфы через PUT не удалось"
        assert response.json()['id'] == movie_id
        assert updated_movie_payload['name'] == response.json()['name']
        assert updated_movie_payload['description'] == response.json()['description']
        assert updated_movie_payload['price'] == response.json()['price']

    def test_delete_movie_by_id(self, api_manager, admin_auth, created_movie):
        '''
        Проверка удаления фильма
        '''

        movie, payload = created_movie
        movie_id = movie['id']

        response = api_manager.movies_api.delete_movie(movie_id, expected_status=200)

        # Валидация ответа от сервера
        schema_path = os.path.join(os.path.dirname(__file__),
                                   "../..",
                                   'schemas',
                                   'delete_movie.json')
        with open(schema_path) as file:
            schema = json.load(file)
        validate(response.json(), schema)  # Валидация ответа от сервера


    def test_delete_without_auth(self, admin_auth, created_movie):
        '''
        Проверка на удаление без авторизации
        '''
        movie, payload = created_movie
        movie_id = movie['id']

        session = requests.Session()
        response = session.delete(f'{MOVIES_URL}{MOVIES_ENDPOINT}/{movie_id}',
                                  headers=HEADERS)
        assert response.status_code == 401, ("Не должно допустить удаление без "
                                             "авторизации")

    def test_delete_non_existing_movie(self, api_manager, admin_auth):
        '''
        Проверка статус-кода ошибки на удаление фильма с несуществующим ID
        '''
        non_existing_id = random.randint(100000, 150000)
        api_manager.movies_api.delete_movie(non_existing_id, expected_status=404)

    def test_create_without_required_field(self, api_manager, admin_auth):
        '''
        Создание фильма без обязательного поля, например, описание description
        '''
        movie_data = DataGenerator.generate_movie_data()
        movie_data.pop('description')
        response = api_manager.movies_api.create_movie(movie_data=movie_data,
                                              expected_status=400)

        assert "error" in response.json() or "message" in response.json(), ("В ответе "
                                                                            "должно быть описание ошибки")

    def test_create_same_movie_twice(self, api_manager, admin_auth, created_movie):
        '''
        Повторное создание фильма, который уже был создан. Проверка корректности
        статус-кода
        '''
        movie, payload = created_movie
        response = api_manager.movies_api.create_movie(movie_data=payload,
                                                       expected_status=409)
        assert "error" in response.json() or "message" in response.json(), ("В ответе должно быть "
                                                         "описаниешибки")






