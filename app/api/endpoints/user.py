from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from typing import TYPE_CHECKING, Annotated
from app.api.endpoints.todo import get_todo_repository
from app.api.schemas.user import UserCreate, UserUpdate, UserFromDB
from app.core.config import settings
from app.db.database import get_async_session
from app.db.usermodel import User
from app.repositories.user_repository import UserRepository, SqlAlchemyUserRepository

user_router = APIRouter(
    prefix="/user",
    tags=["User"]
)

from app.repositories.todo_repository import ToDoRepository


# тут нам нужна функция по инициализации ТуДу-репозитория (для уменьшения количества кода)
async def get_user_repository(session: AsyncSession = Depends(get_async_session)) -> UserRepository:
    return SqlAlchemyUserRepository(session)


# наши роуты стали значительно короче
@user_router.get("/")
async def get_users(repo: UserRepository = Depends(get_user_repository)):
    return await repo.get_users()


# можно заметить, что оба роута зависят от общей функции получения репозитория,
# которая зависит от сессий -> это пример цепочки инъекции зависимостей
@user_router.post("/", response_model=UserFromDB)
async def create_user(user: UserCreate, repo: UserRepository = Depends(get_user_repository)):
    return await repo.create_user(user)


@user_router.post("/login/")
def login(user_data: Annotated[OAuth2PasswordRequestForm, Depends()], repo: UserRepository = Depends(get_user_repository)): # тут логинимся через форму
    user_data_from_db: User = repo.get_user_by_name(user_data.username)
    if user_data_from_db is None or user_data.password != user_data_from_db.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"access_token": settings.create_jwt_token({"sub": user_data.username})}


@user_router.get("/{user_id}", response_model=UserFromDB)
async def get_user_by_id(user_id: int, repo: UserRepository = Depends(get_user_repository)):
    return await repo.get_user_by_id(user_id)


@user_router.put("/update/{user_id}", response_model=UserUpdate)
async def update_user(user_id: int, user: UserUpdate, repo: UserRepository = Depends(get_user_repository)):
    return await repo.update_user(user_id, user)


@user_router.delete("/{user_id}")
async def delete_user(user_id: int, repo: UserRepository = Depends(get_user_repository),
                      todo_repo: ToDoRepository = Depends(get_todo_repository)):
    await todo_repo.delete_by_user_id(user_id)
    return await repo.delete_user(user_id)
