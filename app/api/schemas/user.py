from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    email: str | None = None
    password: str


class UserFromDB(UserCreate):  # будем возвращать из БД - унаследовались от создания и расширили 2 полями
    id: int
    active: bool = False
    jwt_token: str


class UserUpdate(UserCreate):
    username: str | None = None
    email: str | None = None