import uuid
import enum
from sqlalchemy.orm import relationship, Mapped, mapped_column, backref, declarative_base
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import DateTime
from sqlalchemy import UUID, Column, Integer, LargeBinary, String, Date, Boolean, func
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy import Enum

Base = declarative_base()

class Role(enum.Enum):
    admin: str = "admin"
    moderator: str = "moderator"
    user: str = "user"


class AssetType(enum.Enum):
    origin: str = 'origin'
    avatar: str = 'avatar'
    greyscale: str = 'greyscale'
    delete_bg: str = 'delete_bg'
    oil_paint: str = 'oil_paint'
    sepia: str = 'sepia'
    outline: str = 'outline'


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(50))
    email = Column(String(250), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    phone = Column(String(13), unique=True, nullable=True, default=None)
    birthday = Column(Date, nullable=True, default=None)
    created_at = Column("created_at", DateTime, default=func.now())
    avatar = Column(String(255), nullable=True)
    refresh_token = Column(String(255), nullable=True)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    role = Column('role', Enum(Role), default=Role.user)
    confirmed = Column(Boolean, default=False)