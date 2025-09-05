from pydantic import BaseModel, ConfigDict, FilePath
from datetime import datetime
from enum import Enum
from typing import Optional
from models.models import RequestStatus
from schemas.user import UserBase


class RepairRequestUpdate(BaseModel):
    description: Optional[str] = None
    photo_url: Optional[FilePath] = None
    desired_deadline: Optional[datetime] = None


class RepairRequestOut(BaseModel):
    id: int
    description: str
    status: RequestStatus
    photo_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    desired_deadline: Optional[datetime] = None

    user_id: int
    admin_id: Optional[int]

    model_config = ConfigDict(from_attributes=True)


class AdminMessageOut(BaseModel):
    message: str
    created_at: datetime

    admin_id: int
    admin_name: UserBase


class ServiceRecordOut(BaseModel):
    pay: str
    parts_used: str
    warranty_info: str
    data_completed: datetime


class RepairRequestFull(RepairRequestOut):

    admin_message: Optional[AdminMessageOut] = None
    service_record: Optional[ServiceRecordOut] = None
