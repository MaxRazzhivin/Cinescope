import uuid
from sqlalchemy import Column, String, Boolean, DateTime
from typing import Dict, Any
from project.db_models import Base


class UserDBModel(Base):
    __tablename__ = 'users'

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4())) # text в БД
    email = Column(String)  # text в БД
    full_name = Column(String)  # text в БД
    password = Column(String)  # text в БД
    created_at = Column(DateTime)  # timestamp в БД
    updated_at = Column(DateTime)  # timestamp в БД
    verified = Column(Boolean)  # bool в БД
    banned = Column(Boolean)  # bool в БД
    roles = Column(String)  # text в БД (Role enum)

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        return {
            'id': self.id,
            'email': self.email,
            'full_name': self.full_name,
            'password': self.password,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'verified': self.verified,
            'banned': self.banned,
            'roles': self.roles
        }

    def __repr__(self):
        return (f"<User id={self.id} email={self.email} "
                f"name={self.full_name} verified={self.verified} banned={self.banned} "
                f"created_at={self.created_at} updated_at={self.updated_at}>")







