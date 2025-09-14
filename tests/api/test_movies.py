import json
import os
import random

import pytest
import requests
from jsonschema import validate

from conftest import common_user
from constants import MOVIES_URL, MOVIES_ENDPOINT
from models.errors_model import ForbiddenResponse, BadRequestResponse, \
    UnauthorizedResponse, CinemaNotFound, Conflict
from models.movies_model import GetMovies, MoviesFilter, MoviesResponse, \
    PatchMovieRequest


class TestMoviesAPI:
    @pytest.mark.slow
    def test_get_movies(self, common_user):
        """
        Тест на получение списка фильмов
        """
        response = common_user.api.movies_api.get_all_movies(expected_status=200)
        body=response.json()
        response_model = GetMovies(**body)

        assert isinstance(response_model.movies, list), 'Ответ должен быть списком'

        # Валидация ответа от сервера
        schema_path = os.path.join(os.path.dirname(__file__),
                                   "../..",
                                   'schemas',
                                   'get_movies.json')
        with open(schema_path) as file:
            schema = json.load(file)
        validate(response.json(), schema)  # Валидация ответа от сервера

    @pytest.mark.slow
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

        filter_movie = MoviesFilter(**query)

        response = common_user.api.movies_api.get_movies_with_filter(
            query=filter_movie,
            expected_status=200
        )
        body = response.json()
        body_model = GetMovies(**body)

        # базовые проверки
        assert isinstance(body_model.movies, list)

        # 1) цены входят в диапазон
        assert all(min_price <= movie.price <= max_price for movie in
                   body_model.movies)

        # 2) локации соответствуют (если бэкенд возвращает одно значение)
        assert all(movie.location in locations for movie in body_model.movies)

        # 3) жанр совпадает
        assert all(movie.genreId == genre_id for movie in body_model.movies)


    def test_create_movie(self, created_movie):
        '''
        Тест на создание нового фильма
        Получаем из фикстуры created movie
        movie: dict из ответа на создание фильма
        payload: модель PostMovieRequest
        '''
        movie, payload = created_movie
        movie_model = MoviesResponse(**movie) # Валидируем ответ от бэка по модели
        # MoviesResponse

        assert movie_model.name == payload.name


        # Валидация ответа от сервера
        schema_path = os.path.join(os.path.dirname(__file__),
                                   "../..",
                                   'schemas',
                                   'post_movie.json')
        with open(schema_path) as file:
            schema = json.load(file)
        validate(movie, schema)  # Валидация ответа от сервера

    @pytest.mark.slow
    def test_get_movie_by_id(self, created_movie, common_user):
        '''
        Получение инфы про созданный фильм по ID
        Получаем из фикстуры created movie
        movie: dict из ответа на создание фильма
        '''

        movie, _ = created_movie
        movie_id = movie['id'] # Сохраняем id нашего фильма для поиска дальше

        movie_model = MoviesResponse(**movie)  # Валидируем ответ от бэка по модели
        # MoviesResponse после создания фильма

        response = common_user.api.movies_api.get_movie_by_id(movie_id,
                                                           expected_status=200)

        response_model_search_id = MoviesResponse(**response.json()) # Валидируем
        # модель ответа после запроса на поиск кино по id

        # Сравниваем между 2
        # моделями на момент создания и после нахождения по id

        assert response_model_search_id.id == movie_model.id
        assert response_model_search_id.name == movie_model.name
        assert response_model_search_id.description == movie_model.description

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
        Получаем из фикстуры created movie
        movie: dict из ответа на создание фильма
        payload: модель PostMovieRequest
        '''
        movie, payload = created_movie
        movie_id = movie['id'] # Сохраняем ID созданного фильма

        movie_model = MoviesResponse(**movie)  # Валидируем ответ от бэка по модели
        # MoviesResponse после создания фильма

        # Берем данные фильма и вносим изменения
        patch_payload = PatchMovieRequest(
            name=movie_model.name + " Updated",
            description=movie_model.description + " Something new for update",
            price=movie_model.price + random.randint(100, 500)
        )

        response = super_admin.api.movies_api.update_movie(movie_id,
                                                       movie_data=patch_payload,
                                                       expected_status=200)

        model_response_after_patch = MoviesResponse(**response.json())

        # сверяем поля измененные с правками, которые отправляли
        assert model_response_after_patch.name == patch_payload.name
        assert model_response_after_patch.description == patch_payload.description
        assert model_response_after_patch.price == patch_payload.price

        # остальные данные, которые должны остаться без изменений
        assert model_response_after_patch.id == movie_model.id
        assert model_response_after_patch.genreId == movie_model.genreId
        assert model_response_after_patch.location == movie_model.location
        assert model_response_after_patch.published == movie_model.published
        assert model_response_after_patch.imageUrl == movie_model.imageUrl
        assert model_response_after_patch.rating == movie_model.rating


    def test_delete_movie_by_id(self, created_movie, super_admin, common_user):
        '''
        Проверка удаления фильма
        Получаем из фикстуры created movie
        movie: dict из ответа на создание фильма
        payload: модель PostMovieRequest
        '''

        movie, payload = created_movie
        movie_id = movie['id']

        movie_model = MoviesResponse(**movie)  # Валидируем ответ от бэка по модели
        # MoviesResponse после создания фильма

        response = super_admin.api.movies_api.delete_movie(movie_id,
                                                           expected_status=200)

        deleted_movie_model = MoviesResponse(**response.json())
        assert deleted_movie_model.id == movie_model.id
        assert deleted_movie_model.name == movie_model.name
        assert deleted_movie_model.description == movie_model.description

        # убеждаемся, что данный фильм нельзя найти от лица обычного юзера
        common_user.api.movies_api.get_movie_by_id(movie_id, expected_status=404)



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

        получаем из фикстуры created movie
        movie: dict из ответа на создание фильма
        '''

        movie, _ = created_movie
        movie_id = movie["id"]

        # получаем объект пользователя-исполнителя по имени фикстуры
        actor = request.getfixturevalue(actor_fixture)

        response = actor.api.movies_api.delete_movie(movie_id,
                                                 expected_status=expected_status)

        if expected_status == 200:
            deleted_movie_model = MoviesResponse(**response.json())
            assert deleted_movie_model.id == movie_id
        else:
            error_model = ForbiddenResponse(**response.json())
            assert error_model.message == "Forbidden resource"


    def test_user_cannot_create_movie(self, common_user, test_movie):
        '''
        Проверка что обычный юзер не сможет создать фильм
        '''
        response = common_user.api.movies_api.create_movie(test_movie,
                                                         expected_status=403)

        error_model = ForbiddenResponse(**response.json())
        assert error_model.message == "Forbidden resource"

    def test_get_movies_with_filters_wrong_types(self, common_user):
        '''
        Проверка на получение фильмов через фильтры с неверным типом данных
        '''
        query = {
            "minPrice": "abc",  # неверный тип
            "maxPrice": -1,  # error: minPrice must be less than maxPrice
        }
        response = common_user.api.movies_api.get_movies_with_filter(query=query,
                                                          expected_status=400)

        error_model = BadRequestResponse(**response.json())
        assert any("minPrice" in m for m in error_model.message), \
            "В сообщениях об ошибке нет информации про minPrice"




    @pytest.mark.slow
    def test_delete_without_auth(self, created_movie):
        '''
        Проверка на удаление без авторизации
        '''
        movie, payload = created_movie
        movie_id = movie['id']

        session = requests.Session()
        response = session.delete(f'{MOVIES_URL}{MOVIES_ENDPOINT}/{movie_id}')

        UnauthorizedResponse(**response.json())

    def test_delete_non_existing_movie(self, super_admin):
        '''
        Проверка статус-кода ошибки на удаление фильма с несуществующим ID
        '''
        non_existing_id = random.randint(100000, 150000)
        response = super_admin.api.movies_api.delete_movie(non_existing_id,
                                                    expected_status=404)

        error_model = CinemaNotFound(**response.json())
        assert 'Фильм не найден' in error_model.message

    def test_create_without_required_field(self, test_movie, super_admin):
        '''
        Создание фильма без обязательного поля, например, описание description
        test_movie: модель от PostMovieRequest
        '''
        movie_data = test_movie.model_dump().copy()
        movie_data.pop('description')
        response = super_admin.api.movies_api.create_movie(movie_data=movie_data,
                                              expected_status=400)

        error_model = BadRequestResponse(**response.json())

        assert any("description" in m.lower() for m in error_model.message), \
            "В сообщениях об ошибке нет информации про поле, вызвавшее ошибку"

    def test_create_same_movie_twice(self, created_movie, super_admin):
        '''
        Повторное создание фильма, который уже был создан. Проверка корректности
        статус-кода
        '''
        movie, payload = created_movie
        response = super_admin.api.movies_api.create_movie(movie_data=payload,
                                                       expected_status=409)
        error_model = Conflict(**response.json())

        assert error_model.statusCode == 409
        assert error_model.error == "Conflict"
        assert "Фильм с таким названием уже существует" in error_model.message






