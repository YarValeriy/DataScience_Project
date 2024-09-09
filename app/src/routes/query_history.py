from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.database.db import get_db
from src.schemas.schemas import QueryHistoryCreate, QueryHistoryResponse
from src.repository import query_history as repository
from src.services.auth import auth_service
from src.entity.models import User

# Роутер для роботи з історією запитів
router = APIRouter(prefix="/query_history", tags=["Query History"])

# Створення нового запису в історії запитів
@router.post("/", response_model=QueryHistoryResponse, status_code=status.HTTP_201_CREATED)
async def create_query_history(
    body: QueryHistoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    new_query = repository.create_query_history(
        db=db,
        user_id=current_user.id,
        document_id=body.document_id,
        query=body.query,
        response=body.response
    )
    return new_query


# Отримання всієї історії запитів користувача
@router.get("/", response_model=list[QueryHistoryResponse])
async def get_query_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    history = repository.get_user_query_history(db=db, user_id=current_user.id)
    return history


# Видалення запису з історії запитів
@router.delete("/{query_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_query_history(
    query_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    deleted = repository.delete_query_history(db=db, query_id=query_id, user_id=current_user.id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Query not found")
    return None
