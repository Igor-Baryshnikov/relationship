from abc import ABC, abstractmethod

import jwt
import sqlalchemy
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.todo import ToDoCreate, ToDoUpdate
from app.core.config import settings
from app.db.database import get_async_session
from app.db.models import ToDo
from app.db.usermodel import User
from app.repositories.user_repository import UserRepository, SqlAlchemyUserRepository
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_user_from_token(token: str = Depends(oauth2_scheme)) -> str:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload.get(
            "sub")
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_user_repository(session: AsyncSession = Depends(get_async_session)) -> UserRepository:
    return SqlAlchemyUserRepository(session)


class ToDoRepository(ABC):  # это абстрактный интерфейс нашего репозитория
    @abstractmethod
    async def get_todos(self):
        pass

    @abstractmethod
    async def create_todo(self, todo: ToDoCreate, user_repo: UserRepository, current_user: str = Depends(get_user_from_token)) -> ToDo:
        pass

    @abstractmethod
    async def get_todo_by_id(self, todo_id: int) -> ToDo:
        pass

    @abstractmethod
    async def delete_todo(self, todo_id: int, user_repo: UserRepository, current_user: str = Depends(get_user_from_token)):
        pass

    @abstractmethod
    async def update_todo(self, todo_id: int, todo: ToDoUpdate, user_repo: UserRepository,
                          current_user: str = Depends(get_user_from_token)) -> ToDo:
        pass

    @abstractmethod
    async def delete_by_user_id(self, user_id: int):
        pass


class SqlAlchemyToDoRepository(ToDoRepository):  # это его конкретное исполнение для алхимии (можно сделать для peewee, pony и тд, легко поменять способ реализации)
    def __init__(self, session: AsyncSession):  # при инициализации принимает асинхронную сессию
        self.session = session

    # далее, по сути, код из эндпоинтов с предыдущего шага
    async def get_todos(self):
        result = await self.session.execute(select(ToDo))
        return result.scalars().all()

    async def create_todo(self, todo: ToDoCreate, user_repo: UserRepository, current_user: str = Depends(get_user_from_token)) -> ToDo:
        res: User = await user_repo.get_user_by_name(current_user)
        new_todo = ToDo(**todo.model_dump())
        new_todo.user_id = res.id
        self.session.add(new_todo)
        await self.session.commit()
        await self.session.refresh(new_todo)
        return new_todo

    async def get_todo_by_id(self, todo_id: int) -> ToDo:
        result1 = await self.session.execute(select(ToDo).where(ToDo.id == todo_id))
        return result1.scalar_one_or_none()

    async def delete_todo(self, todo_id: int, user_repo: UserRepository, current_user: str = Depends(get_user_from_token)):
        res: User = await user_repo.get_user_by_name(current_user)
        query = sqlalchemy.select(ToDo.user_id).where(ToDo.id == todo_id)
        result = await self.session.execute(query)
        if not res.id == result.scalars().one():
            raise HTTPException(405, "Method Not Allowed")
        query = sqlalchemy.delete(ToDo).where(ToDo.id == todo_id)
        await self.session.execute(query)
        await self.session.commit()
        return "Todo deleted"

    async def update_todo(self, todo_id: int, todo: ToDoUpdate, user_repo: UserRepository,
                          current_user: str = Depends(get_user_from_token)) -> ToDo:
        res: User = await user_repo.get_user_by_name(current_user)
        query = sqlalchemy.select(ToDo.user_id).where(ToDo.id == todo_id)
        result = await self.session.execute(query)
        if not res.id == result.scalars().one():
            raise HTTPException(405, "Method Not Allowed")
        query = sqlalchemy.update(ToDo).where(ToDo.id == todo_id).values(**todo.model_dump())
        await self.session.execute(query)
        await self.session.commit()
        result1 = await self.session.execute(select(ToDo).where(ToDo.id == todo_id))
        return result1.scalar_one_or_none()

    async def delete_by_user_id(self, user_id: int):
        query = sqlalchemy.delete(ToDo).where(ToDo.user_id == user_id)
        await self.session.execute(query)