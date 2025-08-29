from fastapi import Depends, APIRouter, Query
from fastapi.security import OAuth2PasswordRequestForm

from models.models import User
from schemas.user import UserBase, UserOut
from settings import get_db
from tools.auth import  get_current_user, require_admin
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()    


@router.get("/hello")
async def hello_user(
    username: str = Query("Anonymous", description="Ім'я користувача")
):
    return {"message": f"hello {username}"}


@router.get("/user/me")
async def user_me_data(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/user/admin/me")
async def only_for_admin(current_user: User = Depends(require_admin)):
    return {"is admin": current_user}

