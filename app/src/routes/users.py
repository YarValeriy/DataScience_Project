from fastapi import APIRouter, HTTPException, Depends, status, File, Form, UploadFile, Query
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession

from typing import List
from sqlalchemy.orm import Session

from src.entity.models import User, Role
from src.schemas.user import UserResponse
from src.schemas.schemas import UserResponseAll
from src.services.auth import auth_service

from src.repository import users as repositories_users
from src.database.db import get_db
from src.services.roles import RoleChecker

router = APIRouter(prefix='/users', tags=['users'])

allowed_get_all_users = RoleChecker([Role.admin])

@router.get("/me", response_model=UserResponse, dependencies=[Depends(RateLimiter(times=1, seconds=20))])
async def get_current_user(user: User = Depends(auth_service.get_current_user)):
    return user

@router.post("/edit-me", response_model=UserResponse)
async def edit_my_profile(avatar: UploadFile = File(), new_username: str = Form(None), user: User = Depends(auth_service.get_current_user), db: AsyncSession = Depends(get_db)):
    updated_user = await repositories_users.edit_my_profile(avatar, new_username, user, db)
    return updated_user


@router.get("/all", response_model=List[UserResponse], dependencies=[Depends(allowed_get_all_users)])
async def read_all_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    users = await repositories_users.get_users(skip, limit, db)
    return users