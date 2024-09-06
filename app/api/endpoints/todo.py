from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas import todo
from app.api.schemas.todo import ToDoFromDB, ToDoCreate, ToDoUpdate
from app.db.database import get_async_session
from app.repositories.todo_repository import ToDoRepository, SqlAlchemyToDoRepository, get_user_from_token, \
    get_user_repository
from app.repositories.user_repository import UserRepository



todo_router = APIRouter(
    prefix="/todo",
    tags=["ToDo"]
)


# тут нам нужна функция по инициализации ТуДу-репозитория (для уменьшения количества кода)
async def get_todo_repository(session: AsyncSession = Depends(get_async_session)) -> ToDoRepository:
    return SqlAlchemyToDoRepository(session)


# наши роуты стали значительно короче
@todo_router.get("/")
async def get_todos(repo: ToDoRepository = Depends(get_todo_repository)):
    return await repo.get_todos()


# можно заметить, что оба роута зависят от общей функции получения репозитория,
# которая зависит от сессий -> это пример цепочки инъекции зависимостей
@todo_router.post("/", response_model=ToDoFromDB)
async def create_todo(todo: ToDoCreate, repo: ToDoRepository = Depends(get_todo_repository),
                      user_repo: UserRepository = Depends(get_user_repository),
                      current_user: str = Depends(get_user_from_token)):
    return await repo.create_todo(todo, user_repo, current_user)


@todo_router.get("/{todo_id}", response_model=ToDoFromDB)
async def get_todo_by_id(todo_id: int, repo: ToDoRepository = Depends(get_todo_repository)):
    return await repo.get_todo_by_id(todo_id)


@todo_router.put("/update/{todo_id}", response_model=ToDoUpdate)
async def update_todo(todo_id: int, todo: ToDoUpdate, repo: ToDoRepository = Depends(get_todo_repository),
                      user_repo: UserRepository = Depends(get_user_repository), current_user: str = Depends(get_user_from_token)):
    return await repo.update_todo(todo_id, todo, user_repo,current_user)


@todo_router.delete("/{todo_id}")
async def delete_todo(todo_id: int, repo: ToDoRepository = Depends(get_todo_repository),
                      user_repo: UserRepository = Depends(get_user_repository),
                      current_user: str = Depends(get_user_from_token)):
    return await repo.delete_todo(todo_id, user_repo,current_user)
