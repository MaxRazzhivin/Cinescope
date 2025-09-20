from uuid import uuid4

from conftest import super_admin


class TestDatabase:
    def test_db_requests(self, db_helper, created_test_user):
        '''
        Проверяем, что пользователь был создан успешно и его email совпадает с тем,
        который в базе
        '''
        assert created_test_user == db_helper.get_user_by_id(created_test_user.id)
        assert db_helper.user_exists_by_email(created_test_user.email)

    def test_movie(self, test_movie, db_helper, super_admin):
        '''
        Проверяем, что фильма до нас не было такого в БД

        Создаем рандом набор данных для фильма и сохраняем оттуда название, название
        делаем более уникальным, чтобы избежать, что такой фильм уже есть в базе

        uuid4() — генерирует случайный UUID v4.
	    .hex — даёт его в виде 32-символьной шестнадцатеричной строки (без дефисов).
	    [:6] — берём только первые 6 символов, чтобы суффикс был коротким.
	    __ — обычный разделитель для читабельности, можно заменить на - или что угодно.
        '''
        movie_name_unique = f'{test_movie.name}__{uuid4().hex[:6]}'
        assert db_helper.get_movie_by_name(movie_name_unique) is None

        # Создаем фильм через рандомный генератор также, но меняем в нем название на
        # созданное выше уникальное

        # Обновляем в модели фильма из фикстуры test_movie ключ name
        payload = test_movie.model_copy(update={'name': movie_name_unique})

        # Создаем фильм в БД

        created_in_db = db_helper.create_test_movie(payload.model_dump())

        # Проверяем, что такая строка в БД вообще есть
        assert created_in_db.id is not None
        assert created_in_db.name == movie_name_unique

        # Проверяем существование в БД по id
        assert db_helper.movie_exists_by_id(created_in_db.id)
        got_from_db = db_helper.get_movie_by_id(created_in_db.id)
        assert got_from_db is not None and got_from_db.name == movie_name_unique

        # Делаем удаление фильма через API .delete_movie()
        assert super_admin.api.movies_api.delete_movie(created_in_db.id,
                                                       expected_status=(200,204))

        # Проверяем, что запись пропала из БД
        assert db_helper.get_movie_by_id(created_in_db.id) is None

        # Проверяем негативный сценарий по несуществующему id
        assert db_helper.movie_exists_by_id(0) is False