import datetime
import random
import string
from time import timezone

from faker import Faker

faker = Faker()


class DataGenerator:

    # Генератор случайных email-ов
    # string.ascii_lowercase = 'abcdefghijklmnopqrstuvwxyz'
    # string.digits = '0123456789'

    # random.choices(string.ascii_lowercase + string.digits, k=8) = выбирает 8
    # рандомных чисел и букв и возвращает список ['x', '9', 'a', '2', 'h', '7', 'd', '1']

    # ''.join(list) - объединяет в строку, убирает запятые
    # random_string = 'x9a2h7d1'
    @staticmethod
    def generate_random_email():
        random_string = ''.join(random.choices(string.ascii_lowercase +
                                               string.digits, k=8))
        return f"kek{random_string}@gmail.com"

    # Создаем рандомные имя с фамилией с библиотекой Faker
    @staticmethod
    def generate_random_name():
        return f"{faker.first_name()} {faker.last_name()}"

    # Создаем рандомный пароль, соответствующий требованиям
    @staticmethod
    def generate_random_password():
        '''
        Генерация пароля, соответствующего требованиям:
        - Минимум 1 буква.
        - Минимум 1 цифра.
        - Допустимые символы.
        - Длина от 8 до 20 символов.
        '''

        # Гарантируем наличие хотя бы одной ЗАГЛАВНОЙ буквы и одной цифры
        letters = random.choice(string.ascii_uppercase) # Одна рандомная буква
        digits = random.choice(string.digits) # Одна рандомная цифра

        # Дополняем пароль случайными символами из допустимого набора
        special_chars = '?@#$%^&*|:'

        # Создаем строку, которая включает все буквы, цифры и доп символы
        all_chars = string.ascii_lowercase + string.digits + special_chars

        # случайная длина пароля от 6 до 18 символов
        remaining_length = random.randint(6, 18)

        # получаем случайный пароль длиной remaining_length
        remaining_chars = ''.join(random.choices(all_chars, k=remaining_length))

        # перемешиваем пароль для рандомизации
        password = list(letters + digits + remaining_chars)
        random.shuffle(password)

        return ''.join(password)

    @staticmethod
    def generate_movie_data():
        '''
        Генерация случайного фильма
        '''
        return {
            'name': faker.sentence(nb_words=3).rstrip('.'), # случайное название из 3
            # букв и удаление точки в конце имени
            'price': random.randint(50,1000),
            'description': faker.text(max_nb_chars=100), # случайное описание,
            # не более 100 букв
            'location': random.choice(['MSK', 'SPB']),
            'published': random.choice([True, False]),
            'genreId': random.randint(1, 4),
            'rating': random.randint(1, 5),
            'createdAt': datetime.datetime.now(datetime.timezone.utc)
        }

    """
    Добавим метод, который сразу делает рандомные данные,
    которые можно сразу передать в метод создания юзера через БД
    """

    @staticmethod
    def generate_user_data() -> dict:
        """Генерирует данные для тестового пользователя"""
        from uuid import uuid4

        return {
            'id': f'{uuid4()}',  # генерируем UUID как строку
            'email': DataGenerator.generate_random_email(),
            'full_name': DataGenerator.generate_random_name(),
            'password': DataGenerator.generate_random_password(),
            'created_at': datetime.datetime.now(),
            'updated_at': datetime.datetime.now(),
            'verified': False,
            'banned': False,
            'roles': '{USER}'
        }