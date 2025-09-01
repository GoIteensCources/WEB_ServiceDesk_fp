from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, func, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from settings import Base


class RequestStatus(str, Enum):
    NEW = "Нова"
    IN_PROGRESS = "В обробці"
    MESSAGE = "Повідомлення"
    COMPLETED = "Завершено"
    CANCELLED = "Скасовано"


class RepairRequest(Base):
    __tablename__ = "repair_requests"

    id: Mapped[int] = mapped_column(primary_key=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    photo_url: Mapped[str] = mapped_column(String(255), nullable=True)
    status: Mapped[RequestStatus] = mapped_column(
        SQLEnum(RequestStatus), default=RequestStatus.NEW, nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now(), onupdate=func.now()
    )

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    admin_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)

    # Зв'язок з User (той, хто створив заявку)
    user: Mapped["User"] = relationship(
        "User",
        back_populates="repair_requests",
        foreign_keys=[user_id],
        lazy="selectin",
    )

    # Зв'язок з User (адмін, який взяв у роботу)
    admin: Mapped["User"] = relationship(
        "User",
        back_populates="assigned_repair_requests",
        foreign_keys=[admin_id],
        lazy="selectin",
    )

    # Список повідомлень
    messages: Mapped[list["AdminMessage"]] = relationship(
        "AdminMessage",
        back_populates="to_repair_request",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    # Список сервісних записів (може бути кілька)
    service_records: Mapped["ServiceRecord"] = relationship(
        "ServiceRecord",
        back_populates="to_repair_request",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    def __str__(self):
        return f"<RepairRequest {self.id} - {self.status}>"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(254), nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)

    # Заявки, створені користувачем
    repair_requests: Mapped[list["RepairRequest"]] = relationship(
        "RepairRequest",
        back_populates="user",
        foreign_keys="[RepairRequest.user_id]",
        lazy="selectin",
    )

    # Заявки, які закріплені за адміном
    assigned_repair_requests: Mapped[list["RepairRequest"]] = relationship(
        "RepairRequest",
        back_populates="admin",
        foreign_keys="[RepairRequest.admin_id]",
        lazy="selectin",
    )

    # Повідомлення, створені адміном
    admin_messages: Mapped[list["AdminMessage"]] = relationship(
        "AdminMessage",
        back_populates="admin",
        cascade="all, delete-orphan"
    )

    def __str__(self):
        if self.is_admin:
            return f"<Admin> {self.id} - {self.username}"
        return f"<User> {self.id} - {self.username}"


class AdminMessage(Base):
    __tablename__ = "admin_messages"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now()
    )

    request_id: Mapped[int] = mapped_column(ForeignKey("repair_requests.id"), nullable=False)
    admin_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    # зв’язки
    to_repair_request: Mapped["RepairRequest"] = relationship(
        "RepairRequest", back_populates="messages"
    )
    admin: Mapped["User"] = relationship(
        "User", back_populates="admin_messages"
    )


class ServiceRecord(Base):
    __tablename__ = "service_records"

    id: Mapped[int] = mapped_column(primary_key=True)
    pay: Mapped[str] = mapped_column(String(50), nullable=False)
    parts_used: Mapped[str] = mapped_column(Text, nullable=True)
    warranty_info: Mapped[str] = mapped_column(Text, nullable=False)
    data_completed: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now()
    )

    request_id: Mapped[int] = mapped_column(ForeignKey("repair_requests.id"), nullable=False)

    to_repair_request: Mapped["RepairRequest"] = relationship(
        "RepairRequest", back_populates="service_records"
    )

    def __str__(self):
        return f"<ServiceRecord {self.id} - {self.pay}>"