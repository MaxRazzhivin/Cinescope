import json
import os
import random

import pytest
import requests
from jsonschema import validate

from constants import MOVIES_URL, MOVIES_ENDPOINT


class TestMoviesAPI:
    def test_get_movies(self, common_user):
        """
        Тест на получение списка фильмов
        """
        response = common_user.api.movies_api.get_all_movies(expected_status=200)
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


    @pytest.mark.parametrize(
        'min_price,max_price,locations,genre_id',
        [
            (1, 1000, ['MSK'], 1),
            (2, 500, ['SPB'], 2),
            (100, 400, ['MSK', 'SPB'], 3),
        ]
    )
    def test_get_movies_with_filters(self, common_user, min_price, max_price,
                                     locations, genre_id):
        query = {
            'minPrice': min_price,
            'maxPrice': max_price,
            'locations': locations,
            'genreId': genre_id
        }

        response = common_user.api.movies_api.get_movies_with_filter(
            query=query,
            expected_status=200
        )
        body = response.json()

        # базовые проверки
        assert "movies" in body and isinstance(body["movies"], list)
        movies = body["movies"]

        # 1) цены входят в диапазон
        assert all(min_price <= m["price"] <= max_price for m in movies)

        # 2) локации соответствуют (если бэкенд возвращает одно значение)
        assert all(m["location"] in locations for m in movies)

        # 3) жанр совпадает
        assert all(m["genreId"] == genre_id for m in movies)


    def test_create_movie(self, created_movie):
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

    def test_get_movie_by_id(self, created_movie, common_user):
        '''
        Получение инфы про созданный фильм по ID
        '''

        movie, _ = created_movie
        movie_id = movie['id']
        response = common_user.api.movies_api.get_movie_by_id(movie_id,
                                                           expected_status=200)
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


    def test_update_movie(self, created_movie, super_admin):
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

        response = super_admin.api.movies_api.update_movie(movie_id,
                                                       movie_data=updated_movie_payload,
                                                       expected_status=200)

        assert response.status_code == 200, "Обновление инфы через PATCH не удалось"
        assert response.json()['id'] == movie_id
        assert updated_movie_payload['name'] == response.json()['name']
        assert updated_movie_payload['description'] == response.json()['description']
        assert updated_movie_payload['price'] == response.json()['price']

    def test_delete_movie_by_id(self, created_movie, super_admin):
        '''
        Проверка удаления фильма
        '''

        movie, payload = created_movie
        movie_id = movie['id']

        response = super_admin.api.movies_api.delete_movie(movie_id,
                                                           expected_status=200)

        # Валидация ответа от сервера
        schema_path = os.path.join(os.path.dirname(__file__),
                                   "../..",
                                   'schemas',
                                   'delete_movie.json')
        with open(schema_path) as file:
            schema = json.load(file)
        validate(response.json(), schema)  # Валидация ответа от сервера

    @pytest.mark.parametrize(
        'actor_fixture,expected_status', [
            ('super_admin', 200),
            ('admin_user', 403),
            ('common_user', 403)
        ]
    )
    def test_delete_movie_by_id_with_roles(self, created_movie, request,
                                           actor_fixture, expected_status):
        '''
        Проверка удаления фильма под разными ролями.
        Вначале создаем фильм через super_admin фикстуру created_movie
        Затем через request.getfixturevalue(actor_fixture) вытаскиваем фикстуры по
        очереди для параметризации - super_admin, admin_user, common_user
        '''

        movie, _ = created_movie
        movie_id = movie["id"]

        # получаем объект пользователя-исполнителя по имени фикстуры
        actor = request.getfixturevalue(actor_fixture)

        actor.api.movies_api.delete_movie(movie_id,
                                                 expected_status=expected_status)

    def test_user_cannot_create_movie(self, common_user, test_movie):
        '''
        Проверка что обычный юзер не сможет создать фильм
        '''
        common_user.api.movies_api.create_movie(test_movie, expected_status=403)

    def test_get_movies_with_filters_wrong_types(self, common_user):
        '''
        Проверка на получение фильмов через фильтры с неверным типом данных
        '''
        query = {
            "minPrice": "abc",  # неверный тип
            "maxPrice": -1,  # error: minPrice must be less than maxPrice
        }
        common_user.api.movies_api.get_movies_with_filter(query=query,
                                                          expected_status=400)


    def test_delete_without_auth(self, created_movie):
        '''
        Проверка на удаление без авторизации
        '''
        movie, payload = created_movie
        movie_id = movie['id']

        session = requests.Session()
        response = session.delete(f'{MOVIES_URL}{MOVIES_ENDPOINT}/{movie_id}')
        assert response.status_code == 401, ("Не должно допустить удаление без "
                                             "авторизации")

    def test_delete_non_existing_movie(self, super_admin):
        '''
        Проверка статус-кода ошибки на удаление фильма с несуществующим ID
        '''
        non_existing_id = random.randint(100000, 150000)
        super_admin.api.movies_api.delete_movie(non_existing_id, expected_status=404)

    def test_create_without_required_field(self, test_movie, super_admin):
        '''
        Создание фильма без обязательного поля, например, описание description
        '''
        movie_data = test_movie.copy()
        movie_data.pop('description')
        response = super_admin.api.movies_api.create_movie(movie_data=movie_data,
                                              expected_status=400)

        assert "error" in response.json() or "message" in response.json(), ("В ответе "
                                                                            "должно быть описание ошибки")

    def test_create_same_movie_twice(self, created_movie, super_admin):
        '''
        Повторное создание фильма, который уже был создан. Проверка корректности
        статус-кода
        '''
        movie, payload = created_movie
        response = super_admin.api.movies_api.create_movie(movie_data=payload,
                                                       expected_status=409)
        assert "error" in response.json() or "message" in response.json(), ("В ответе должно быть "
                                                         "описание ошибки")






