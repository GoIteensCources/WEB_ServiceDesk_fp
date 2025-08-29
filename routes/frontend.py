from fastapi import Depends, APIRouter, Query, Request
from fastapi.templating import Jinja2Templates

from models.models import User
from tools.auth import  get_current_user, require_admin


router = APIRouter()    
templates = Jinja2Templates(directory="templates")


@router.get("/", include_in_schema=False)
async def index(request: Request, 
                # current_user: User = Depends(get_current_user), 
                error:str|None = None):
    return templates.TemplateResponse("index.html", {"request": request, 
                                                    #  "current_user": current_user, 
                                                     "error": error})
