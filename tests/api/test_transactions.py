from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from models.movies_model import MoviesResponse
from project.db_models.transactions import AccountTransactionTemplate
from utils.data_generator import DataGenerator


def transfer_money(session: Session, from_account: str, to_account: str, amount: int):
    """
    Переводит деньги с одного счета на другой.
    :param session: Сессия SQLAlchemy.
    :param from_account_id: ID счета, с которого списываются деньги.
    :param to_account_id: ID счета, на который зачисляются деньги.
    :param amount: Сумма перевода.
    """

    # Получаем счета
    from_row = session.query(AccountTransactionTemplate).filter_by(
        user=from_account).one()
    to_row = session.query(AccountTransactionTemplate).filter_by(
        user=to_account).one()

    # Проверяем, что на счете достаточно средств
    if from_row.balance < amount:
        raise ValueError("Недостаточно средств на счете")

    # Выполняем перевод
    from_row.balance -= amount
    to_row.balance += amount

    # Сохраняем изменения
    session.commit()

def test_accounts_transaction_successful(db_session: Session):
    # Подготовка к тесту - Arrange
    # Создаем новые записи в базе данных

    stan = AccountTransactionTemplate(user=f"Stan_{uuid4().hex[:6]}",
                                      balance=1000)
    bob = AccountTransactionTemplate(user=f"Bob_{uuid4().hex[:6]}",
                                     balance=500)

    # Добавляем записи в сессию
    db_session.add_all([stan, bob])
    # Фиксируем изменения в базе данных
    db_session.commit()

    # Проверяем начальные балансы
    assert stan.balance == 1000
    assert bob.balance == 500

    try:
        # Act
        # Выполняем перевод 200 единиц от stan к bob
        transfer_money(db_session,
                       from_account=stan.user,
                       to_account=bob.user,
                       amount=200)

        # Assert
        # Проверяем, что балансы изменились
        assert stan.balance == 800
        assert bob.balance == 700

        # Для достоверности - повторный запрос из БД
        same_stan = db_session.get(AccountTransactionTemplate, stan.user)
        same_bob = db_session.get(AccountTransactionTemplate, bob.user)
        assert same_stan.balance == 800
        assert same_bob.balance == 700


    except Exception as e:
        # Если произошла ошибка, откатываем транзакцию
        db_session.rollback()  # откат всех введеных нами изменений
        pytest.fail(f"Ошибка при переводе денег: {e}")

    finally:
        # Teardown
        # Удаляем данные для тестирования из базы
        db_session.delete(stan)
        db_session.delete(bob)
        # Фиксируем изменения в базе данных
        db_session.commit()


def test_accounts_transfer_insufficient_funds(db_session: Session):
    # Arrange
    eric = AccountTransactionTemplate(user=f"Eric{uuid4().hex[:6]}",
                                      balance=1000)
    clyde = AccountTransactionTemplate(user=f"Clyde{uuid4().hex[:6]}",
                                     balance=500)

    db_session.add_all([eric, clyde])
    db_session.commit()

    try:
        # Act
        with pytest.raises(ValueError, match='Недостаточно средств'):
            transfer_money(db_session, from_account=eric.user,
                           to_account=clyde.user,
                           amount=2000)

        db_session.rollback()

        # Arrange
        # Проверяем повторно баланс из БД после отката операции
        same_eric=db_session.get(AccountTransactionTemplate, eric.user)
        same_clyde=db_session.get(AccountTransactionTemplate, clyde.user)

        # Assert
        assert same_eric.balance == 1000
        assert same_clyde.balance == 500

    finally:
        # Teardown
        db_session.delete(same_eric or eric)
        db_session.delete(same_clyde or clyde)
        db_session.commit()



def test_delete_movie_by_id(super_admin, db_helper, common_user):
    '''
    Проверка удаления фильма
    '''
    # Arrange
    payload = DataGenerator.generate_movie_data()
    created = db_helper.create_test_movie(payload)
    movie_id = created.id

    # Проверка, что фильм появился в БД по такому ID
    common_user.api.movies_api.get_movie_by_id(movie_id, expected_status=200)
    assert db_helper.get_movie_by_id(movie_id) is not None

    # Act - удаляем через API
    super_admin.api.movies_api.delete_movie(movie_id, expected_status=(200,204))

    # Assert - сверяемся, что фильма больше нет в БД
    common_user.api.movies_api.get_movie_by_id(movie_id, expected_status=(400,404))
    assert db_helper.get_movie_by_id(movie_id) is None

