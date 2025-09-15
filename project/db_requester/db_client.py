import psycopg2
from psycopg2.extras import RealDictCursor

from resources.db_creds import MoviesDbCreds


def connect_to_postgres():
    """Функция для подключения к PostgreSQL базе данных - вариант через контекстный
    менеджер with, он сам закроет сессию и курсор при выходе из блока"""

    try:
        # Подключение к базе данных
        with psycopg2.connect(**MoviesDbCreds.as_dict()) as connection:

            print("Подключение успешно установлено")

            # Второй контекстный менеджер для курсора
            with connection.cursor(cursor_factory=RealDictCursor) as cursor:

                # Вывод информации о PostgreSQL сервере
                print("Информация о сервере PostgreSQL:")
                print(connection.get_dsn_parameters(), "\n")

                # Выполнение SQL-запроса
                cursor.execute("SELECT version();")

                # Получение результата
                record = cursor.fetchone()
                print("Вы подключены к -", record[0], "\n")

    except Exception as error:
        print("Ошибка при работе с PostgreSQL:", error)

if __name__ == "__main__":
    connect_to_postgres()