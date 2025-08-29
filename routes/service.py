from fastapi import Depends, APIRouter, Query
from fastapi.security import OAuth2PasswordRequestForm

from models.models import User
from schemas.user import UserBase, UserOut
from settings import get_db
from tools.auth import  get_current_user, require_admin
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()    
