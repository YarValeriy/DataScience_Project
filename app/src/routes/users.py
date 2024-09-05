from fastapi import (
    APIRouter,
    Form,
    HTTPException,
    Depends,
    Path,
    status,
    File,
    UploadFile,
)
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession

from typing import List
from sqlalchemy.orm import Session

from src.entity.models import User, Role

from src.schemas.schemas import UserUpdateSchema, RoleUpdateSchema, SearchUserResponse, AssetType
from src.services.auth import auth_service
from src.services.photo import CloudPhotoService

from src.repository import users as repositories_users
from src.database.db import get_db
from src.services.roles import RoleChecker, admin_access, moderator_access
from src.conf.config import settings
from src.exceptions.exceptions import RETURN_MSG


router = APIRouter(prefix="/users", tags=["users"])

# allowed_get_all_users = RoleChecker([Role.admin])


@router.get(
    "/me",
    response_model=SearchUserResponse,
    dependencies=[Depends(RateLimiter(times=1, seconds=20))],
)
async def get_current_user(user: User = Depends(auth_service.get_current_user)):
    """
    The get_current_user function is a dependency that returns the current user.
    Args:
        user:

    Returns:

    """
    return user


# @router.post("/edit-me", response_model=UserResponse)
# async def edit_my_profile(avatar: UploadFile = File(), new_username: str = Form(None), user: User = Depends(auth_service.get_current_user), db: AsyncSession = Depends(get_db)):
#     updated_user = await repositories_users.edit_my_profile(avatar, new_username, user, db)
#     return updated_user


@router.put("/")
async def update_user(
    body: UserUpdateSchema,
    db: AsyncSession = Depends(get_db),
    cur_user: User = Depends(auth_service.get_current_user),
):
    """
    The update_user function updates a user's information.
    Args:
        body:
        db:
        cur_user:

    Returns:

    """
    user = await repositories_users.update_user(cur_user.id, body, db)
# auth_service.get_current_user would not allow this to happen
    # if cur_user is None:
    #     raise HTTPException(
    #         status_code=status.HTTP_404_NOT_FOUND,
    #         detail="User not Found",
    #     )
    return user


@router.put("/avatar")
async def update_avatar(
    file: UploadFile = File(),
    current_user: User = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    The update_avatar function updates the avatar of a user.
    Args:
        file:
        current_user:
        db:

    Returns:

    """
    public_id = f"{settings.cloudinary_app_prefix}/users/{current_user.username}"
    asset = CloudPhotoService.upload_photo(file=file, public_id=public_id)
    url = CloudPhotoService.get_photo_url(public_id=public_id, asset=asset)
    url = CloudPhotoService.transformate_photo(url=url, asset_type=AssetType.avatar)
    user = await repositories_users.update_avatar(current_user.email, url, db)
    return user