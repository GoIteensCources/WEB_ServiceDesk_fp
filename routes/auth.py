from fastapi import Depends, APIRouter
from fastapi.security import OAuth2PasswordRequestForm

from models.models import User
from schemas.user import UserBase, UserOut
from settings import get_db
from tools.auth import authenticate_user, create_access_token, credentials_exception
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.post("/token")
async def generate_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise credentials_exception

    data_payload = {"sub": str(user.id), "email": user.email, "is_admin": user.is_admin}
    access_token = create_access_token(payload=data_payload)
    print(access_token)
    return {"access_token": access_token, "token_type": "bearer"}



@router.post("/register", response_model=UserOut)
async def create_user(user: UserBase, db: AsyncSession = Depends(get_db)):
    new_user = User(**user.model_dump())
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user
