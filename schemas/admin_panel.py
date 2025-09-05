from pydantic import BaseModel
from datetime import date
from models import RequestStatus  # 🔥 імпортуємо enum


class RequestBase(BaseModel):
    title: str
    description: str | None = None
    desired_deadline: date | None = None


class RequestCreate(RequestBase):
    pass


class RequestResponse(RequestBase):
    id: int
    status: RequestStatus

    class Config:
        orm_mode = True


class RequestStatusUpdate(BaseModel):
    new_status: RequestStatus = RequestStatus.IN_PROGRESS
