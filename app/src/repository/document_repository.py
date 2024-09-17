from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql import text
from sqlalchemy import update
from fastapi import Depends, HTTPException
from src.database.db import get_db
from src.entity.models import Document
from src.schemas.schemas import DocumentCreate
from src.entity.models import Document
from typing import Tuple, List, Dict, Optional
import json
import numpy as np
from datetime import datetime
import logging

async def create_document_entry(document_data: DocumentCreate, db: AsyncSession) -> int:
    """
    Create a new document entry in the database.
    """
    new_document = Document(
        title=document_data.title,
        author=document_data.author,
        comment=document_data.comment,
        original_file_name=document_data.original_file_name,
        status=document_data.status,
        upload_date=datetime.utcnow()
    )

    db.add(new_document)
    await db.commit()
    await db.refresh(new_document)
    return new_document.document_id



async def get_all_documents(db: AsyncSession):
    """
    Fetches all documents from the database using SQLAlchemy ORM.

    Args:
        db (AsyncSession): The database session.

    Returns:
        List[Document]: A list of all documents.
    """
    # Using SQLAlchemy's ORM interface to fetch all documents
    result = await db.execute(select(Document))
    return result.scalars().all()


async def update_document_status(document_id: int, status: str, db: AsyncSession):
    """
    Update the status of a document in the database.
    """
    async with db as session:
        stmt = (
            update(Document)
            .where(Document.document_id == document_id)
            .values(status=status)
        )
        await session.execute(stmt)
        await session.commit()


def validate_vector_format(vector):
    """
    Validates the format of the vector to ensure it is a list of floats or a list of lists of floats.

    Args:
        vector (list or np.ndarray): The vector to validate.

    Returns:
        list: The validated vector as a list.

    Raises:
        ValueError: If the vector is not in the correct format.
    """
    if isinstance(vector, np.ndarray):
        vector = vector.tolist()  # Convert to a list

    if not (isinstance(vector, list) and
            all(isinstance(i, (float, int)) or
                (isinstance(i, list) and all(isinstance(j, (float, int)) for j in i))
                for i in vector)):
        raise ValueError("Vector is not in the correct format. It should be a list of floats or a list of lists.")

    return vector


async def update_document_vectors(
        document_id: int,
        summary: Optional[str],
        summary_vector: list,
        full_text_vector: list,
        db: AsyncSession
):
    """
    Updates the document's summary, summary vector, and full text vector in the database.

    Args:
        document_id (int): The ID of the document to update.
        summary (Optional[str]): The summary text.
        summary_vector (Optional[list]): The vector representation of the summary.
        full_text_vector (Optional[list]): The vector representation of the full text.
        db (AsyncSession): The database session.

    Raises:
        ValueError: If document is not found or vector validation fails.
    """
    try:
        # Fetch the document by ID
        document = await db.execute(select(Document).where(Document.document_id == document_id))
        document = document.scalar_one_or_none()
        if not document:
            raise ValueError("Document not found")

        # Update the summary and summary vector if provided
        if summary_vector is not None:
            # print(f"Updating document {document_id} with summary vector")
            summary_vector = validate_vector_format(summary_vector)
            summary_vector_json = json.dumps(summary_vector)  # Convert to JSON
            stmt = (
                update(Document)
                .where(Document.document_id == document_id)
                .values(
                    summary=summary if summary else "",  # Use empty string if no summary provided
                    summary_vector=summary_vector_json
                )
            )
            await db.execute(stmt)
            await db.commit()

        # Update the full text vector if provided
        if full_text_vector is not None:
            print(f"Updating document {document_id} with full text vector")
            full_text_vector = validate_vector_format(full_text_vector)
            full_text_vector_json = json.dumps(full_text_vector)  # Convert to JSON
            stmt = (
                update(Document)
                .where(Document.document_id == document_id)
                .values(
                    full_text_vector=full_text_vector_json
                )
            )
            await db.execute(stmt)
            await db.commit()

    except Exception as e:
        print(f"Error while updating vectors: {e}")
        raise ValueError(f"Failed to update document vectors in the database: {e}")

async def get_documents_by_ids(document_ids: List[int], db: AsyncSession) -> List[Document]:
    """
    Fetch documents by their IDs from the database.

    Args:
        document_ids (List[int]): List of document IDs to fetch.
        db (AsyncSession): The SQLAlchemy AsyncSession object for database access.

    Returns:
        List[Document]: A list of Document objects.
    """
    try:
        # Query to fetch documents by their IDs
        stmt = select(Document).where(Document.document_id.in_(document_ids))
        result = await db.execute(stmt)
        documents = result.scalars().all()
        return documents
    except Exception as e:
        raise ValueError(f"Failed to fetch documents by IDs: {str(e)}")

async def get_document_by_id(document_id: int, db: AsyncSession) -> Document:
        document = await db.execute(select(Document).where(Document.document_id == document_id))
        return document.scalar()
