from sqlalchemy import BigInteger, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING
from app.db.database import Base


if TYPE_CHECKING:
    from app.db.models import ToDo


class User(Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(40), index=True)
    email: Mapped[str] = mapped_column(String(50), index=True)
    password: Mapped[str] = mapped_column(String(50), index=True)
    active: Mapped[bool] = mapped_column(default=True)
    jwt_token: Mapped[str] = mapped_column(String)
    todos: Mapped[list["ToDo"]] = relationship(back_populates="user")
