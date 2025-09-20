# Модель для таблицы accounts_transaction_template
from sqlalchemy import Column, String, Integer

from project.db_models import Base


class AccountTransactionTemplate(Base):
    __tablename__ = 'accounts_transaction_template'
    user = Column(String, primary_key=True)
    balance = Column(Integer, nullable=False)