from libgravatar import Gravatar
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from src.entity.models import User
from src.schemas.schemas import UserSchema, UserUpdateSchema, RoleUpdateSchema
import redis.asyncio as redis
from sqlalchemy.future import select

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import UploadFile
from src.conf.config import settings
from src.entity.models import BlacklistToken
from time import time
from asyncio import sleep


async def get_user_by_email(email: str, db: Session) -> User:
    return db.query(User).filter(User.email == email).first()


async def get_user_by_id(user_id: int, db: Session) -> User:
    return db.query(User).filter(User.id == user_id).first()


async def create_user(body: UserSchema, db: Session) -> User:
    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as e:
        print(e)
    new_user = User(**body.model_dump(), avatar=avatar)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


# async def change_role(user_id: int, body: RoleUpdateSchema, db: Session):
#     stmt = select(User).filter_by(id=user_id)
#     result = db.execute(stmt)
#     user = result.scalar_one_or_none()
#     if user is None:
#         return None
#     user.role = body.role
#     db.commit()
#     db.refresh(user)
#     return user


async def update_user(user_id: int, body: UserUpdateSchema, db: Session):
    stmt = select(User).filter_by(id=user_id)
    result = db.execute(stmt)
    user = result.scalar_one_or_none()
    if user is None:
        return None
    user.username = body.username
    user.phone = body.phone
    user.birthday = body.birthday
    db.commit()
    db.refresh(user)
    return user


async def update_avatar(email: str, url: str, db: Session):
    user = await get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    db.refresh(user)
    return user


async def confirmed_email(email: str, db: Session) -> None:
    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()


async def update_token(user: User, token: str | None, db: Session) -> None:
    user.refresh_token = token
    db.commit()


BLACKLISTED_TOKENS = "blacklisted_tokens"

r = redis.Redis(
    host=settings.redis_host,
    port=settings.redis_port,
    db=0,
    encoding="utf-8",
    decode_responses=True,
)


# async def is_token_blacklisted(token: str) -> bool:
#     return await r.sismember(BLACKLISTED_TOKENS, token)


async def dell_from_black_list(expired, token: str, db: AsyncSession) -> None:
    bl_token = db.query(BlacklistToken).filter(BlacklistToken.token == token).first()
    time_now = time()
    time_for_sleep = expired - time_now
    await sleep(time_for_sleep)
    db.delete(bl_token)
    db.commit()
