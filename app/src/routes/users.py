from fastapi import (
    APIRouter,
    HTTPException,
    Depends,
    # Path,
    status,
    # File,
    # UploadFile,
)
# from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession

# from typing import List
from sqlalchemy.orm import Session

from src.entity.models import User  #Role

from src.schemas.schemas import UserUpdateSchema, SearchUserResponse, UserDeleteSchema
# from src.services.photo import CloudPhotoService

from src.repository import users as repositories_users
from src.database.db import get_db
# from src.services.roles import RoleChecker, admin_access, moderator_access
# from src.conf.config import settings
from src.exceptions.exceptions import RETURN_MSG
from src.services.auth import auth_service


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

@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    body: UserDeleteSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    if not auth_service.verify_password(body.password, current_user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
    
    deleted = await repositories_users.delete_user(current_user.id, db)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    await auth_service.log_user_deletion(current_user.email)
    return None