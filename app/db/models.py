import datetime

from typing import TYPE_CHECKING
from sqlalchemy import BigInteger, DateTime, func, String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


if TYPE_CHECKING:
    from .usermodel import User

class ToDo(Base):  # обязательно наследуем все модели от нашей Base-метатаблицы
    __tablename__ = "todo"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(40), index=True)
    description: Mapped[str] = mapped_column(Text, default="nothing")
    completed: Mapped[bool] = mapped_column(default=False)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("user.id"))
    user: Mapped["User"] = relationship(back_populates="todos")
