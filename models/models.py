from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from settings import Base


class RepairRequest(Base):
    __tablename__ = "repair_requests"

    id: Mapped[int] = mapped_column(primary_key=True)

    # TODO

    admin_messages: Mapped[list["AdminMessage"]] = relationship(back_populates="repair_request")
    service_records: Mapped["ServiceRecord"] = relationship(back_populates="repair_request")


# Модель Note
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(100), nullable=False)  # Зберігаємо хеш пароля
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)

    repair_requests: Mapped[list["RepairRequest"]] = relationship(back_populates="user")
    assigned_repair_requests: Mapped[list["RepairRequest"]] = relationship(back_populates="admin")
    
    admin_messages: Mapped[list["AdminMessage"]] = relationship(back_populates="admin")

    def __str__(self):
        if self.is_admin:
            return f"<Admin> з {self.id} та {self.username}"
        return f"<User> з {self.id} та {self.username}. "


class AdminMessage(Base):
    __tablename__ = "admin_messages"

    id: Mapped[int] = mapped_column(primary_key=True, index= True)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())

    request_id:Mapped[int] = mapped_column( ForeignKey("repair_requests.id"), nullable=False)
    admin_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    # зв’язки
    repair_request = relationship("RepairRequest", backref="admin_messages")
    admin = relationship("User", backref="admin_messages")


class ServiceRecord(Base):
    __tablename__ = "service_records"

    id: Mapped[int] = mapped_column(primary_key=True)
    pay: Mapped[str] = mapped_column(String(50), nullable=False)
    parts_used: Mapped[str] = mapped_column(Text, nullable=True)
    warranty_info: Mapped[str] = mapped_column(Text, nullable=False)
    data_completed: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())

    request_id: Mapped[int] = mapped_column(ForeignKey("repair_requests.id"), nullable=False)
    repair_request = relationship("RepairRequest", backref="service_records")

    def __str__(self):
        return f"<ServiceRecord> з {self.id} та {self.pay}"
