import datetime

from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from settings import Base


# Модель Note
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    password: Mapped[str] = mapped_column(
        String(100), nullable=False
    )  # Зберігаємо хеш пароля

    def __str__(self):
        return f"<User> з {self.id} та {self.username}"
