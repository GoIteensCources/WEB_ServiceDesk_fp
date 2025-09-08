from pydantic import BaseModel, ConfigDict
from datetime import date
from models import RequestStatus  # 🔥 імпортуємо enum


class RequestBase(BaseModel):
    title: str
    description: str | None = None
    desired_deadline: date | None = None

    model_config = ConfigDict(from_attributes=True)


class RequestCreate(RequestBase):
    pass


class RequestResponse(RequestBase):
    id: int
    status: RequestStatus


class RequestStatusUpdate(BaseModel):
    new_status: RequestStatus = RequestStatus.IN_PROGRESS
