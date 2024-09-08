import enum
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql.sqltypes import DateTime
from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey, DateTime, func
from sqlalchemy import Enum
from datetime import datetime

Base = declarative_base()

class Role(enum.Enum):
    admin: str = "admin"
    # moderator: str = "moderator"
    user: str = "user"


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

    # Зворотний зв'язок до QueryHistory
    queries = relationship("QueryHistory", back_populates="user")


class QueryHistory(Base):
    __tablename__ = "query_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))  # ForeignKey на таблицю користувачів
    document_id = Column(Integer)  # Якщо потрібна прив'язка до документа
    query = Column(String, nullable=False)  # Запит користувача
    response = Column(String, nullable=False)  # Відповідь LLM
    timestamp = Column(DateTime, default=datetime.utcnow)  # Час запиту
    
    user = relationship("User", back_populates="queries")  # Відношення до моделі користувача
