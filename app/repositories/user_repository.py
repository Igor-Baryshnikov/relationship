from abc import ABC, abstractmethod

import jwt
import sqlalchemy
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.user import UserCreate, UserUpdate
from app.core.config import settings
from app.db.usermodel import User


class UserRepository(ABC):  # это абстрактный интерфейс нашего репозитория
    @abstractmethod
    async def get_users(self):
        pass

    @abstractmethod
    async def create_user(self, user: UserCreate) -> User:
        pass

    @abstractmethod
    async def get_user_by_id(self, user_id: int) -> User:
        pass

    @abstractmethod
    async def delete_user(self, user_id: int):
        pass

    @abstractmethod
    async def update_user(self, user_id: int, user: UserUpdate) -> User:
        pass

    @abstractmethod
    async def get_user_by_name(self, username: str) -> User:
        pass

    @abstractmethod
    async def get_user_by_jwt(self, email: str) -> User:
        pass


class SqlAlchemyUserRepository(UserRepository):  # это его конкретное исполнение для алхимии (можно сделать для peewee, pony и тд, легко поменять способ реализации)
    def __init__(self, session: AsyncSession):  # при инициализации принимает асинхронную сессию
        self.session = session

    # далее, по сути, код из эндпоинтов с предыдущего шага
    async def get_users(self):
        result = await self.session.execute(select(User))
        return result.scalars().all()

    async def create_user(self, user: UserCreate) -> User:
        new_user = User(**user.model_dump())
        new_user.jwt_token = settings.create_jwt_token({"sub": user.username})
        self.session.add(new_user)
        await self.session.commit()
        await self.session.refresh(new_user)
        return new_user

    async def get_user_by_id(self, user_id: int) -> User:
        result1 = await self.session.execute(select(User).where(User.id == user_id))
        return result1.scalar_one_or_none()

    async def delete_user(self, user_id: int):
        query = sqlalchemy.select(User).where(User.id == user_id)
        result = await self.session.execute(query)
        if not result.scalars().one():
            return "Not Found"
        query = sqlalchemy.delete(User).where(User.id == user_id)
        await self.session.execute(query)
        await self.session.commit()
        return "User deleted"

    async def update_user(self, user_id: int, user: UserUpdate) -> User:
        query = sqlalchemy.update(User).where(User.id == user_id).values(**user.model_dump())
        await self.session.execute(query)
        await self.session.commit()
        result1 = await self.session.execute(select(User).where(User.id == user_id))
        return result1.scalar_one_or_none()

    async def get_user_by_name(self, username: str) -> User:
        query = sqlalchemy.select(User).where(User.username == username)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_user_by_jwt(self, jwt_token: str) -> User:
        query = sqlalchemy.select(User).where(User.jwt_token == jwt_token)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()