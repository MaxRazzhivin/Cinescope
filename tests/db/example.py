class TestDatabase:
    def test_db_requests(self, db_helper, created_test_user):
        assert created_test_user == db_helper.get_user_by_id(created_test_user.id)
        assert db_helper.user_exists_by_email("api1@gmail.com")

    def test_movie_not_exists_in_db_before_creating_by_us(self, test_movie, db_helper):
        movie_name = test_movie.model_dump()['name']
        assert db_helper.get_movie_by_name(movie_name) is None

    def test_movie_requests(self, db_helper, created_test_movie):
        got_movie_from_db = db_helper.get_movie_by_id(created_test_movie.id)

        # Проверяем, что такая строка в БД вообще есть
        assert got_movie_from_db is not None

        # Проверяем, что строка соответствует той, что создавали
        assert got_movie_from_db.id == created_test_movie.id
        assert got_movie_from_db.name == created_test_movie.name

        # Проверяем по id, что такой фильм присутствует в БД
        assert db_helper.movie_exists_by_id(created_test_movie.id)

        # Проверяем негативный сценарий по несуществующему id
        assert db_helper.movie_exists_by_id(14110) is False