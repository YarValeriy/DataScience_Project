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
import torch
import json
import numpy as np
from datetime import datetime
import logging
from src.services.summary_service import clean_text
from src.services.vector_service import vectorize_text_llm

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


async def get_document_by_id(document_id: int, db: AsyncSession) -> Document:
    """
    Retrieve a document by its ID from the database.
    """
    result = await db.execute(select(Document).where(Document.document_id == document_id))
    document = result.scalar_one_or_none()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


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

    if isinstance(vector, np.ndarray):
        vector = vector.tolist()  # Convert to a list

    # Check for a list of lists or a flat list of floats/ints
    if not (isinstance(vector, list) and
            all(isinstance(i, (float, int)) or
                (isinstance(i, list) and all(isinstance(j, (float, int)) for j in i))
                for i in vector)):
        raise ValueError("Vector is not in the correct format. It should be a list of floats or a list of lists.")

    return vector


async def update_document_vectors(
        document_id: int,
        summary: str,
        summary_vector: list,
        full_text_vector: list,
        db: AsyncSession
):
    """Updates the document's summary, summary vector, and full text vector in the database."""

    try:
        document = await db.execute(select(Document).where(Document.document_id == document_id))
        document = document.scalar_one_or_none()
        if not document:
            raise ValueError("Document not found")

        # Validate and convert vectors if provided
        if summary_vector is not None:
            summary_vector = validate_vector_format(summary_vector)
            summary_vector_list = summary_vector.tolist() if isinstance(summary_vector, np.ndarray) else summary_vector
            summary_vector_json = json.dumps(summary_vector_list)
            stmt = (
                update(Document)
                .where(Document.document_id == document_id)
                .values(
                    summary=summary,  # Use empty string if no summary provided
                    summary_vector=summary_vector_json,
                )
            )
            await db.execute(stmt)
            await db.commit()

        if full_text_vector is not None:
            full_text_vector = validate_vector_format(full_text_vector)
            full_text_vector_list = full_text_vector.tolist() if isinstance(full_text_vector,
                                                                            np.ndarray) else full_text_vector
            full_text_vector_json = json.dumps(full_text_vector_list)
            stmt = (
                update(Document)
                .where(Document.document_id == document_id)
                .values(
                    full_text_vector=full_text_vector_json,
                )
            )
            await db.execute(stmt)
            await db.commit()
    except Exception as e:
        raise ValueError(f"Failed to update document vectors in the database: {e}")


async def fetch_relevant_documents(query_text: str, search_scope: Optional[List[int]], db: AsyncSession):
   """
    Fetch relevant documents from the database based on a search query.

    Args:
        query_text (str): The search query text.
        search_scope(List[int]): list of document IDs
        # context_type(str): "full_text" or "summary"
        db (AsyncSession): The database session.

    Returns:
        List[Tuple[int, float]]: List of document IDs and their similarity scores.
    """
   # Vectorize the query text
   cleaned_query = clean_text(query_text)
   query_vector = vectorize_text_llm(cleaned_query)
   query_vector = np.array(query_vector, dtype=float).flatten()

   try:
       # Fetch all documents if search_scope is empty
       if not search_scope:
           documents = await get_all_documents(db)
       else:
           # Ensure search_scope is a list of document IDs
           documents = await get_documents_by_ids(search_scope, db)

       similarities = []
       for doc in documents:
           if doc.full_text_vector is None:
               continue

           # Handle the document vector conversion and similarity calculation
           try:
               doc_vector = np.array(json.loads(doc.full_text_vector), dtype=float).flatten()
               similarity = np.dot(query_vector, doc_vector) / (
                           np.linalg.norm(query_vector) * np.linalg.norm(doc_vector))
               similarities.append((doc.document_id, similarity))
           except Exception as e:
               logging.error(f"Error processing document {doc.document_id}: {e}")
               continue

       # Extract document IDs from sorted similarities
       sorted_similarities = sorted(similarities, key=lambda x: x[1], reverse=True)
       relevant_document_ids = [doc_id for doc_id, _ in sorted_similarities]  # Extract IDs only

       return relevant_document_ids

   except Exception as e:
       raise HTTPException(status_code=500, detail=f"Failed to fetch relevant documents: {str(e)}")


async def search_document(query_text: str, db: AsyncSession) -> dict:

    """
    Fetch relevant documents based on the query vector using cosine similarity.

    Args:
        query_text (str): The string representation of the query text.
        db (AsyncSession): The database session.

    Returns:
        Dict "results": Dictionary of document IDs and their similarity scores.
    """
    try:
        # Clean and vectorize the query text
        cleaned_query = clean_text(query_text)
        query_vector = vectorize_text_llm(cleaned_query)
        query_vector = np.array(query_vector, dtype=float).flatten()  # Convert to 1D array

        # Fetch all document vectors from the database
        documents = await get_all_documents(db)
        similarities = []

        for doc in documents:
            if doc.full_text_vector is None:
                continue

            try:
                # Convert vector from JSON string if needed
                doc_vector = np.array(
                    json.loads(doc.full_text_vector) if isinstance(doc.full_text_vector, str) else doc.full_text_vector,
                    dtype=float).flatten()
            except (ValueError, TypeError, json.JSONDecodeError) as e:
                continue

            # Calculate cosine similarity
            query_norm = np.linalg.norm(query_vector)
            doc_norm = np.linalg.norm(doc_vector)
            if query_norm != 0 and doc_norm != 0:
                similarity = np.dot(query_vector, doc_vector) / (query_norm * doc_norm)
                similarities.append((doc.document_id, similarity))

        # Sort the documents by similarity score in descending order
        sorted_similarities = sorted(similarities, key=lambda x: x[1], reverse=True)

        return {"results": sorted_similarities}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


async def retrieve_context_from_documents(
    document_ids: List[int],
    context_type: str,
    db: AsyncSession
) -> str:
    """
    Retrieve context (full text or summary) from the documents based on document IDs.

    Args:
        document_ids (List[int]): List of document IDs.
        context_type (str): Type of context to retrieve ('full_text' or 'summary').
        db (AsyncSession): Database session.

    Returns:
        combined_context(str): Dictionary with document ID as key and context as value.
    """
    try:
        # Fetch documents based on IDs
        documents = await db.execute(select(Document).where(Document.document_id.in_(document_ids)))
        documents = documents.scalars().all()

        # Extract the appropriate context (full_text or summary) based on the context_type
        context_data = []
        for doc in documents:
            if context_type == "full_text":
                context_data.append(doc.full_text or "")  # Use empty string if full_text is None
            elif context_type == "summary":
                context_data.append(doc.summary or "")  # Use empty string if summary is None
            else:
                raise ValueError(f"Invalid context_type: {context_type}")

        # Combine context data into a single string
        combined_context = " ".join(context_data)
        return combined_context

    except Exception as e:
        logging.error(f"Error during context retrieval: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve context from documents: {str(e)}")



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
