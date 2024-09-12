from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql.sqltypes import DateTime
from sqlalchemy import JSON
from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey, DateTime, func, Enum, Text
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

    # Relationship to QueryHistory
    queries = relationship("QueryHistory", back_populates="user", cascade="all, delete-orphan")

    # Add this relationship to fix the error
    documents = relationship("Document", back_populates="user", cascade="save-update")

class QueryHistory(Base):
    __tablename__ = "query_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    document_id = Column(Integer)
    query = Column(String, nullable=False)
    response = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="queries")

class Document(Base):
    __tablename__ = "documents"

    document_id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    author = Column(String(255), nullable=True)
    comment = Column(String, nullable=True)
    original_file_name = Column(String(255), nullable=False)
    status = Column(String(50), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    upload_date = Column(DateTime, default=datetime.utcnow)
    summary = Column(String, nullable=True)
    summary_vector = Column(JSON, nullable=True)    # Field for summary text vectors
    full_text_vector = Column(JSON, nullable=True)  # Field for full text vectors
    full_text = Column(Text, nullable=True)  # Field to store the full text

    user = relationship("User", back_populates="documents")

    # Зв'язок з таблицею користувачів
    # user_id = Column(Integer, ForeignKey("users.id"))
    # document_id = Column(Integer, ForeignKey("document_texts.id"), nullable=True)  # Зв'язок з документами
    # query = Column(String, nullable=False)  # Запит користувача
    # response = Column(String, nullable=False)  # Відповідь LLM
    # timestamp = Column(DateTime, default=datetime.utcnow)  # Час запиту

    # Відношення до таблиці користувачів та документів
    # user = relationship("User", back_populates="queries")
    # document = relationship("DocumentText")
