from fastapi import Depends, APIRouter, HTTPException, Query, status
from sqlalchemy import select

from models.models import AdminMessage, RepairRequest, RequestStatus, ServiceRecord, User
from schemas.admin_panel import RequestStatusUpdate
from schemas.repairs import AdminMessageIn, AdminMessageOut, RepairRequestOut, ServiceRecordCreate

from settings import get_db
from tools.auth import  require_admin
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter(prefix="/admin")


@router.get("/user/admin/me")
async def only_for_admin(current_user_admin: User = Depends(require_admin)):
    return {"is admin": current_user_admin}


@router.put("/{repair_id}/change/status", response_model=RepairRequestOut)
async def change_request_status(
    repair_id: int,
    status_update: RequestStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user_admin: User = Depends(require_admin),
):
    stmt = select(RepairRequest).filter(RepairRequest.id == repair_id)
    request = await db.scalar(stmt)

    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Request not found"
        )

    if (
        request.status == RequestStatus.NEW
        and status_update.new_status == RequestStatus.IN_PROGRESS
    ):
        request.admin_id = current_user_admin.id

    request.status = status_update.new_status
    await db.commit()
    await db.refresh(request)

    return request


@router.get("/repairs", response_model=list[RepairRequestOut])
async def get_all_requests_status_new(
    new: bool = Query(True),
    db: AsyncSession = Depends(get_db),
    current_user_admin: User = Depends(require_admin),
):

    stmt = select(RepairRequest)
    if new:
        stmt = stmt.where(RepairRequest.status == RequestStatus.NEW)

    result = await db.scalars(stmt)
    requests = result.all()
    return requests


@router.get("/self/repairs", response_model=list[RepairRequestOut])
async def get_all_requests_status_cmi(
    active: bool = Query(True),
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(require_admin),
):

    stmt = select(RepairRequest).where(RepairRequest.admin_id == current_admin.id)
    
    if active:
        stmt = stmt.filter(RepairRequest.status == RequestStatus.IN_PROGRESS or 
                           RepairRequest.status == RequestStatus.MESSAGE)
  

    result = await db.scalars(stmt)
    requests = result.all()
    return requests


@router.post("/admin/repair/{repair_id}/change/comment", response_model=AdminMessageOut)
async def create_admin_message(
    repair_id: int,
    message: AdminMessageIn,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(require_admin),
):
    admin_message = AdminMessage(
        message=message.message,
        request_id=repair_id,
        admin_id=current_admin.id,
)

    db.add(admin_message)
    await db.commit()
    await db.refresh(admin_message)

    return admin_message


@router.post("/repair/{repair_id}/change/service_garanty", response_model=RepairRequestOut)
async def create_service_record_with_garanty(
        repair_id: int,
        service_data: ServiceRecordCreate,
        db: AsyncSession = Depends(get_db),
        current_admin: User = Depends(require_admin),
):
   
    stmt = select(RepairRequest).filter(RepairRequest.id == repair_id)
    request = await db.scalar(stmt)

    if not request:
        raise HTTPException(status_code = 404, detail="Не знайдено")


    new_service = ServiceRecord(
        pay=service_data.pay,
        parts_used=service_data.parts_used,
        warranty_info=service_data.warranty_info,
        request_id=repair_id
    )

    db.add(new_service)
    request.status = RequestStatus.COMPLETED

    await db.commit()
    await db.refresh(request)

    return request
