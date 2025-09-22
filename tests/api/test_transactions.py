import random
from uuid import uuid4
import allure
import pytest
from sqlalchemy.orm import Session
from project.db_models.transactions import AccountTransactionTemplate
from utils.data_generator import DataGenerator

@allure.step('Перевод {amount} ед. со счета {from_account} на счет {to_account}')
@allure.description('Переводит деньги с одного счета на другой')
def transfer_money(session: Session, from_account: str, to_account: str, amount: int):
    """
    :param session: Сессия SQLAlchemy.
    :param from_account: ID счета, с которого списываются деньги.
    :param to_account: ID счета, на который зачисляются деньги.
    :param amount: Сумма перевода.
    """

    with allure.step(" Получаем счета"):
        from_row = session.query(AccountTransactionTemplate).filter_by(
            user=from_account).one()
        to_row = session.query(AccountTransactionTemplate).filter_by(
            user=to_account).one()

    with allure.step("Проверяем, что на счете достаточно средств"):
        if from_row.balance < amount:
            raise ValueError("Недостаточно средств на счете")

    with allure.step("Выполняем перевод"):
        from_row.balance -= amount
        to_row.balance += amount

    with allure.step("Сохраняем изменения"):
        session.commit()

@allure.epic("Тестирование транзакций")
@allure.feature("Тестирование транзакций между счетами")
@allure.story('Успешный перевод средств между счетами')
@allure.severity(allure.severity_level.CRITICAL)
@allure.label('qa_name', 'Max Andreich')
@allure.title('Перевод 200 ед. Stan -> Bob')
def test_accounts_transaction_successful(db_session: Session):
    # Подготовка к тесту - Arrange
    with allure.step('Создаем счета Stan и Bob'):

        stan = AccountTransactionTemplate(user=f"Stan_{uuid4().hex[:6]}",
                                          balance=1000)
        bob = AccountTransactionTemplate(user=f"Bob_{uuid4().hex[:6]}",
                                         balance=500)

    with allure.step('Добавляем записи в сессию'):
        db_session.add_all([stan, bob])
    with allure.step('Фиксируем изменения в базе данных'):
        db_session.commit()

    with allure.step('Проверяем начальные балансы'):
        assert stan.balance == 1000
        assert bob.balance == 500

    try:
        # Act
        with allure.step('Выполняем перевод 200 единиц от Stan к Bob'):
            transfer_money(db_session,
                       from_account=stan.user,
                       to_account=bob.user,
                       amount=200)

        # Assert
        with allure.step('Проверяем, что балансы в БД изменились корректно'):
            stan_db = db_session.get(AccountTransactionTemplate, stan.user)
            bob_db = db_session.get(AccountTransactionTemplate, bob.user)
            assert stan_db.balance == 800
            assert bob_db.balance == 700


    except Exception as e:
        with allure.step('Если произошла ошибка, откатываем транзакцию'):
            db_session.rollback()  # откат всех введеных нами изменений
            pytest.fail(f"Ошибка при переводе денег: {e}")

    finally:
        # Teardown
        with allure.step("Чистим за собой данные"):
            db_session.delete(stan)
            db_session.delete(bob)
        with allure.step("Фиксируем изменения в базе данных"):
            db_session.commit()

@allure.epic("Тестирование транзакций")
@allure.feature("Тестирование транзакций между счетами")
@allure.story('Отказ в переводе при недостатке средств')
@allure.severity(allure.severity_level.CRITICAL)
@allure.label('qa_name', 'Max Andreich')
@allure.title('Отказ перевода: недостаточно средств')
def test_accounts_transfer_insufficient_funds(db_session: Session):
    # Arrange
    with allure.step('Создаем счет для Eric и Clyde'):
        eric = AccountTransactionTemplate(user=f"Eric{uuid4().hex[:6]}",
                                          balance=1000)
        clyde = AccountTransactionTemplate(user=f"Clyde{uuid4().hex[:6]}",
                                         balance=500)
    with allure.step('Добавляем этих господ в сессию'):
        db_session.add_all([eric, clyde])
    with allure.step('Сохраняем изменения'):
        db_session.commit()

    try:
        # Act
        with allure.step('''Пытаемся совершить перевод 2000 ед. - ожидаем ошибку 
        ValueError'''):
            with pytest.raises(ValueError, match='Недостаточно средств'):
                transfer_money(db_session, from_account=eric.user,
                               to_account=clyde.user,
                               amount=2000
                               )

        # Arrange
        with allure.step(
                'Проверяем повторно баланс из БД после отката операции'):
            eric_db=db_session.get(AccountTransactionTemplate, eric.user)
            clyde_db=db_session.get(AccountTransactionTemplate, clyde.user)
            # Assert
            assert eric_db.balance == 1000
            assert clyde_db.balance == 500

    finally:
        # Teardown
        with allure.step('Чистим данные после себя'):
            db_session.delete(eric)
            db_session.delete(clyde)
        with allure.step('Сохраняем изменения'):
            db_session.commit()


@allure.epic('Фильмы')
@allure.feature('Удаление фильма')
@allure.story('Удаление фильма через API удаляет запись в БД')
@allure.severity(allure.severity_level.BLOCKER)
@allure.label('qa_name', 'Max Andreich')
@allure.title('Удаление фильма по ID (API -> DB)')
@allure.description('Проверка удаления фильма через API - удаляет запись в БД')
def test_delete_movie_by_id(super_admin, db_helper, common_user):
    # Arrange
    with allure.step('Готовим данные для фильма через генератор и создаем запись в БД'):
        payload = DataGenerator.generate_movie_data()
        created = db_helper.create_test_movie(payload)
        movie_id = created.id

    with allure.step('Проверка, что фильм появился в БД по такому ID'):
        common_user.api.movies_api.get_movie_by_id(movie_id, expected_status=200)
        assert db_helper.get_movie_by_id(movie_id) is not None

    # Act
    with allure.step('Удаляем через API от прав суперадмина'):
        super_admin.api.movies_api.delete_movie(movie_id, expected_status=(200,204))

    # Assert -
    with allure.step('Сверяемся, что фильма больше нет в БД и ответ 400/404'):
        common_user.api.movies_api.get_movie_by_id(movie_id, expected_status=(400,404))
        assert db_helper.get_movie_by_id(movie_id) is None

@allure.title('Тест с перезапусками')
@pytest.mark.flaky(reruns=3)
def test_with_retries(delay_between_retries):
    with allure.step('Шаг 1: Проверка случайного значения'):
        result = random.choice([True, False])
        assert result, "Тест упал, потому что результат False"
