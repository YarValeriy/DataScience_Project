from fastapi import (
    APIRouter,
    # HTTPException,
    Depends,
    # Path,
    # status,
    # File,
    # UploadFile,
)
# from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession

# from typing import List
# from sqlalchemy.orm import Session

from src.entity.models import User  #Role

from src.schemas.schemas import UserUpdateSchema, SearchUserResponse #AssetType, RoleUpdateSchema
from src.services.auth import auth_service
# from src.services.photo import CloudPhotoService

from src.repository import users as repositories_users
from src.database.db import get_db
# from src.services.roles import RoleChecker, admin_access, moderator_access
# from src.conf.config import settings
from src.exceptions.exceptions import RETURN_MSG


router = APIRouter(prefix="/users", tags=["users"])

# allowed_get_all_users = RoleChecker([Role.admin])


@router.get(
    "/me",
    response_model=SearchUserResponse,
    # dependencies=[Depends(RateLimiter(times=1, seconds=20))],
)
async def get_current_user(user: User = Depends(auth_service.get_current_user)):
    return user

@router.put("/")
async def update_user(
    body: UserUpdateSchema,
    db: AsyncSession = Depends(get_db),
    cur_user: User = Depends(auth_service.get_current_user),
):

    user = await repositories_users.update_user(cur_user.id, body, db)
# auth_service.get_current_user would not allow this to happen
    # if cur_user is None:
    #     raise HTTPException(
    #         status_code=status.HTTP_404_NOT_FOUND,
    #         detail="User not Found",
    #     )
    return user

