from datetime import datetime
from logging import config
import os
from fastapi import (
    Body,
    Depends,
    APIRouter,
    File,
    Form,
    HTTPException,
    Query,
    UploadFile,
)
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select

from models.models import RepairRequest, User
from schemas.repairs import (
    RepairRequestFull,
    RepairRequestOut,

)

from settings import get_db, api_config
from tools.auth import get_current_user
from sqlalchemy.ext.asyncio import AsyncSession

from tools.file_upload import save_upload_file

router = APIRouter(prefix="/account")


@router.post("/create_repair_request", response_model=RepairRequestOut)
async def create_repair_request(
    description: str = Form(...),
    photos: list[UploadFile] = File(None),  # кілька фото
    desired_deadline: datetime = Body(None, examples=[datetime.now()]),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    saved_photos = []

    if photos:
        # асинхронно зберігаємо кожен файл
        for photo in photos:
            saved_path = await save_upload_file(
                photo, dest_dir=api_config.STATIC_FILES_DIR
            )
            if saved_path:
                saved_photos.append(saved_path)

    # Створюємо новий запис у БД
    new_request = RepairRequest(
        description=description,
        photo_url=",".join(saved_photos) if saved_photos else None,
        user_id=current_user.id,
        desired_deadline=desired_deadline,
    )
    db.add(new_request)
    await db.commit()
    await db.refresh(new_request)

    return new_request


@router.get("/repair_request/{request_id}", response_model=RepairRequestFull)
async def get_repair_request(
    request_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    result = await db.execute(
        select(RepairRequest).where(RepairRequest.id == request_id,
                                    RepairRequest.user_id ==current_user.id)
    )
    repair_request = result.scalar()

    if not repair_request:
        raise HTTPException(status_code=404, detail="Request not found")

    return repair_request


@router.get("/repair_requests/my", response_model=list[RepairRequestOut])
async def get_all_requests(
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    s = select(RepairRequest).where(RepairRequest.user_id == current_user.id)
    result = await db.scalars(s)
    requests = result.all()
    return requests


@router.patch("/repair_request/{request_id}", response_model=RepairRequestOut)
async def update_repair_request(
    request_id: int,
    photos: list[UploadFile] = File(None),
    description: str | None = Form(None),
    desired_deadline: str | None = Form(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    result = await db.execute(
        select(RepairRequest)
        .where(RepairRequest.id == request_id, 
               RepairRequest.user_id == current_user.id)
    )
    repair_request = result.scalar_one_or_none()

    if not repair_request:
        raise HTTPException(status_code=404, detail="Request not found")

    if description:
        repair_request.description = description
    
    if desired_deadline:
        repair_request.desired_deadline = datetime.fromisoformat(desired_deadline)

    if photos:
        # 1) видаляємо старі фото
        if repair_request.photo_url:
            for old_path in repair_request.photo_url.split(","):
                if os.path.exists(old_path):
                    os.remove(old_path)

        # 2) створюємо директорію для фото
        save_dir = os.path.join(api_config.STATIC_FILES_DIR, str(request_id))
        os.makedirs(save_dir, exist_ok=True)

        # 3) зберігаємо нові фото
        new_paths = []
        for photo in photos:
            saved_path = await save_upload_file(
                photo, dest_dir=api_config.STATIC_FILES_DIR
            )
            if saved_path:
                new_paths.append(saved_path)

        # 4) оновлюємо модель
        repair_request.photo_url = ",".join(new_paths)

    await db.commit()
    await db.refresh(repair_request)

    return repair_request


@router.delete("/repair_request/{request_id}", status_code=204)
async def delete_repair_request(
    request_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    sw = select(RepairRequest).where(RepairRequest.id == request_id)
    result = await db.scalar(sw)
    
    if not result:
        raise HTTPException(status_code=404, detail="Request not found")

    if result.user_id == current_user.id:
        await db.delete(result)
        await db.commit()
