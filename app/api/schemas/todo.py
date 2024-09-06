import datetime

from pydantic import BaseModel


class ToDoCreate(BaseModel):
    title: str
    description: str | None = None


class ToDoFromDB(ToDoCreate):  # будем возвращать из БД - унаследовались от создания и расширили 2 полями
    id: int
    user_id: int
    completed: bool | None = False


class ToDoUpdate(ToDoCreate):
    completed: bool | None = False