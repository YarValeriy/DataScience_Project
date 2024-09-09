from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey, Text, DateTime, Enum, func
from datetime import datetime
import enum

Base = declarative_base()

class Role(enum.Enum):
    admin: str = "admin"
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
    role = Column(Enum(Role), default=Role.user)
    confirmed = Column(Boolean, default=False)

    queries = relationship("QueryHistory", back_populates="user")
    documents = relationship("DocumentText", back_populates="user")


class DocumentText(Base):
    __tablename__ = "document_texts"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    filename = Column(String(255), nullable=False)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=func.now())

    user = relationship("User", back_populates="documents")


class QueryHistory(Base):
    __tablename__ = "query_history"

    id = Column(Integer, primary_key=True, index=True)
    # Зв'язок з таблицею користувачів
    user_id = Column(Integer, ForeignKey("users.id"))
    document_id = Column(Integer, ForeignKey("document_texts.id"), nullable=True)  # Зв'язок з документами
    query = Column(String, nullable=False)  # Запит користувача
    response = Column(String, nullable=False)  # Відповідь LLM
    timestamp = Column(DateTime, default=datetime.utcnow)  # Час запиту

    # Відношення до таблиці користувачів та документів
    user = relationship("User", back_populates="queries")
    document = relationship("DocumentText")
