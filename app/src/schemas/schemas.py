# import uuid
# import enum
from typing import Dict, Hashable, List, Optional, Annotated, TypeVar
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, EmailStr, PastDate, PlainSerializer, Strict, conset, UUID4
from src.entity.models import Role #User #AssetType
from datetime import date


class UserSchema(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=5, max_length=50)


class UserUpdateSchema(BaseModel):
    username: Optional[str] = Field(min_length=3, max_length=40)
    phone: Optional[str] = Field(min_length=10, max_length=13)
    birthday: Optional[date] 

class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RoleUpdateSchema(BaseModel):
    role: Role

class UserDb(BaseModel):
    id: int = 1
    username: str
    email: str
    phone: str | None
    birthday: date | None
    created_at: datetime
    avatar: str
    role: Role

    model_config = ConfigDict(from_attributes=True)


class UserResponse(BaseModel):
    user: UserDb
    detail: str = "User successfully created"


class SearchUserResponse(BaseModel):
    id: int
    username: str
    email: str
    phone: str | None
    birthday: date | None
    created_at: datetime
    avatar: str
    role: Role
    model_config = ConfigDict(from_attributes=True)


class UserResponseAll(BaseModel):
    user: UserDb

    model_config = ConfigDict(from_attributes=True)


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RequestEmail(BaseModel):
    email: EmailStr


class UserNameResponceSchema(BaseModel):
    username:str


UserNameString = Annotated[UserNameResponceSchema, PlainSerializer(
    lambda x: x.username, return_type=str, when_used="unless-none")] 

