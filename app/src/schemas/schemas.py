# import uuid
# import enum
from typing import Dict, Hashable, List, Optional, Annotated, TypeVar
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, EmailStr, PastDate, PlainSerializer, Strict, conset, UUID4
from src.entity.models import Role #User #AssetType
from datetime import date, datetime


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

class UserDeleteSchema(BaseModel):
    password: str


# Базова схема для історії запитів
class QueryHistoryBase(BaseModel):
    document_id: Optional[int] = None
    query: str
    response: str


# Схема для створення історії запиту
class QueryHistoryCreate(QueryHistoryBase):
    pass


# Схема для відповіді з історією запиту
class QueryHistoryResponse(QueryHistoryBase):
    id: int
    timestamp: datetime

    class Config:
        orm_mode = True

# Base schema for Document
class DocumentBase(BaseModel):
    title: str = Field(..., max_length=255)
    author: Optional[str] = Field(None, max_length=255)
    comment: Optional[str] = None
    original_file_name: str = Field(..., max_length=255)

# Schema for creating a Document
class DocumentCreate(DocumentBase):
    status: Optional[str] = Field("processing", max_length=50)

# Schema for updating a Document
class DocumentUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    author: Optional[str] = Field(None, max_length=255)
    comment: Optional[str] = None
    status: Optional[str] = Field(None, max_length=50)

# Schema representing a Document in the database
class DocumentInDB(DocumentBase):
    document_id: int
    user_id: Optional[int]
    upload_date: datetime

    class Config:
        orm_mode = True

# Schema for returning a Document response
class DocumentResponse(DocumentInDB):
    pass

