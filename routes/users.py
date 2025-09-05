from fastapi import Depends, APIRouter, File, Form, HTTPException, Query, UploadFile
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select

from models.models import RepairRequest, User
from schemas.repairs import RepairRequestOut, RepairRequestUpdate
from schemas.user import UserBase, UserOut
from settings import get_db, api_config
from tools.auth import  get_current_user, require_admin
from sqlalchemy.ext.asyncio import AsyncSession

from tools.file_upload import save_upload_file

router = APIRouter(prefix="/account")    


@router.post("/create_repair_request", response_model=RepairRequestOut)
async def create_repair_request(
    description: str = Form(...),
    photos: list[UploadFile] = File(None),   # кілька фото
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    saved_photos = []

    if photos:
        # асинхронно зберігаємо кожен файл
        for photo in photos:
            saved_path = await save_upload_file(photo, dest_dir=api_config.STATIC_FILES_DIR)
            if saved_path:
                saved_photos.append(saved_path)

    # Створюємо новий запис у БД
    new_request = RepairRequest(
        description=description,
        photo_url=",".join(saved_photos) if saved_photos else None,
        user_id = current_user.id
    )
    db.add(new_request)
    await db.commit()
    await db.refresh(new_request)

    return new_request


@router.patch("/repair_request/{request_id}", response_model=RepairRequestOut)
async def update_repair_request(
        request_id: int,
        request_data: RepairRequestUpdate,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):

    result = await db.execute(
        select(RepairRequest)
        .where(RepairRequest.id == request_id)
        .where(RepairRequest.user_id == current_user.id)
    )
    repair_request = result.scalar_one_or_none()
    
    if not repair_request:
        return repair_request
    
    if not repair_request.user_id == current_user.id: 
        raise HTTPException(status_code=403, detail="Not for your")
    
    if request_data.description:
        repair_request.description = request_data.description

    # if request_data.photo_url:
    #     # TODO видаляємо старе фото і зберігаємо нову
    #     repair_request.photo_url = request_data.photo_url

    await db.commit()
    await db.refresh(repair_request)

    return repair_request



@router.delete("/repair_request/{request_id}", status_code=204)
async def delete_repair_request(request_id: int, 
                                db: AsyncSession = Depends(get_db),
                                current_user: User = Depends(get_current_user)):
    sw = select(RepairRequest).where(RepairRequest.id == request_id)
    result = await db.scalar(sw)
    if not result:
        raise HTTPException(status_code=404, detail="Request not found")
    
    if result.user_id == current_user.id:    
        await db.delete(result)
        await db.commit()


    