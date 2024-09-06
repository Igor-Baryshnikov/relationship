import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_async_session
from app.repositories.user_repository import UserRepository, SqlAlchemyUserRepository

user_router = APIRouter(
    prefix="/reg",
    tags=["Registration"]
)