from typing import Optional, List
from fastapi import APIRouter, Depends, UploadFile, HTTPException, File, Query
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.db import get_db
from src.repository.document_repository import create_document_entry, get_document_by_id, update_document_vectors, get_all_documents, fetch_relevant_documents, search_document, retrieve_context_from_documents
from src.services.pdf_service import process_pdf
from src.services.vector_service import vectorize_text_llm
from src.services.summary_service import  generate_summary, clean_text, generate_answer_based_on_context
from src.schemas.schemas import DocumentCreate
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import numpy as np
import json
import logging
from enum import Enum

class ContextType(str, Enum):
    FULL_TEXT = "full_text"
    SUMMARY = "summary"

class SearchScopeScope(str, Enum):
    ALL = "all_docs"
    LISTED = "listed_docs"

def validate_search_scope(
    search_option: SearchScopeScope,
    search_scope: Optional[List[int]] = None
) -> Optional[List[int]]:
    """
    Validator function to check if search_scope is provided when required.
    """
    if search_option == SearchScopeScope.LISTED and not search_scope:
        raise HTTPException(
            status_code=400, detail="Please provide a list of document IDs for search scope."
        )
    return search_scope

router = APIRouter()

@router.post("/documents/")
async def upload_document(
    title: str,
    file: UploadFile = File(...),
    author: Optional[str] = None,
    comment: Optional[str] = None,
    status: Optional[str] = "processing",
    db: AsyncSession = Depends(get_db)
):
    try:
        # Extract the original file name from the UploadFile object
        original_file_name = file.filename

        # Process the PDF file to extract text
        extracted_text = await process_pdf(file)
        # Clean the extracted text
        # cleaned_text = clean_text(extracted_text)

        # # Generate a summary and vectorize it
        # summary, summary_vector = generate_summary(cleaned_text)

        # Create a document entry in the database
        document_data = DocumentCreate(
            title=title,
            author=author,
            comment=comment,
            original_file_name=original_file_name,
            status=status
        )
        document_id = await create_document_entry(document_data, db)

        # Fetch the document after creation
        document = await get_document_by_id(document_id, db)
        # Update the document with the extracted full text
        document.full_text = extracted_text
        db.add(document)
        await db.commit()

        return {"document_id": document_id, "message": "Document uploaded successfully",
                "extracted_text": extracted_text}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@router.post("/convert-text-to-vector")
async def convert_text_to_vector(
    document_id: int = Query(..., description="ID of the document to vectorize"),
    db: AsyncSession = Depends(get_db)
):
    try:
        # Retrieve the document by ID
        document = await get_document_by_id(document_id, db)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")

        # Clean the input text
        cleaned_text = clean_text(document.full_text)

        # Vectorize the text
        text_vector_list = vectorize_text_llm(cleaned_text)


        # Update the document vector in the database
        document.full_text_vector = text_vector_list
        await update_document_vectors(
            document_id=document_id,
            summary=None,
            summary_vector=None,
            full_text_vector=document.full_text_vector,
            db=db
        )


        return {"document_id": document_id, "full_text_vector": text_vector_list}

    except ValueError as e:
        logging.error(f"Error in text-to-vector conversion: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    except Exception as e:
        logging.error(f"Unexpected error in text-to-vector conversion: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")


@router.post("/generate-summary")
async def generate_document_summary(
    document_id: int = Query(..., description="ID of the document to summarize"),
    max_length: int = Query(100, description="Maximum length per 1024 tokens of the document"),
    min_length: int = Query(30, description="Minimum length per 1024 tokens of the document"),
    db: AsyncSession = Depends(get_db)
):
    """Generates and updates the summary and vector for a given document."""
    if max_length <= min_length:
        raise ValueError("max_length must be greater than min_length.")

    try:
        # Fetch the document by ID
        document = await get_document_by_id(document_id, db)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")

        # Clean the input text
        cleaned_text = clean_text(document.full_text)

        # Generate summary and vector for the provided text
        summary = generate_summary(cleaned_text, max_length=max_length, min_length=min_length)
        summary_vector = vectorize_text_llm(summary)  # Returns a list

        # Update the document with the summary
        document.summary = summary
        document.summary_vector = summary_vector

        # Update document summary in the database
        await update_document_vectors(
            document_id=document_id,
            summary=document.summary,
            summary_vector=document.summary_vector,
            full_text_vector=None,
            db=db
        )

        # Return the response with summary and vector
        return {
            "document_id": document_id,
            "summary": summary,
            "summary_vector": summary_vector  # This is a list
        }
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")



@router.post("/search-document/")
async def search_document_endpoint(query_text: str, db: AsyncSession = Depends(get_db)):
    try:
        # Fetch relevant documents using the repository method
        search_results = await search_document(query_text, db)

        # Access the 'results' key from the search_results dictionary
        sorted_similarities = search_results.get("results", [])

        # Return the sorted similarities
        return {"results": sorted_similarities}

    except Exception as e:
        logging.error(f"Error during document search: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@router.post("/answer-question/")
async def answer_question(
    question: str,
    search_option: SearchScopeScope = SearchScopeScope.ALL,
    search_scope: Optional[List[int]] = Depends(validate_search_scope),
    context_type: ContextType = ContextType.FULL_TEXT,
    db: AsyncSession = Depends(get_db)
):
    """
    Request answer to question based on collected documents.
    """
    try:
        # Determine whether to search the entire database or a list of specific documents
        if search_option == SearchScopeScope.ALL:
            search_scope = None  # No document restriction, search all documents

        # Fetch relevant documents using the repository method
        relevant_documents = await fetch_relevant_documents(query_text=question, search_scope=search_scope, db=db)

        # Handle case where no relevant documents are found
        if not relevant_documents:
            return {"relevant_documents": [], "answer": "No relevant context found to answer the question."}

        # Retrieve context for relevant documents
        context_data = await retrieve_context_from_documents(relevant_documents, context_type, db)

        # Generate the answer based on the context
        answer = generate_answer_based_on_context(question, context_data)

        return {"relevant_documents": relevant_documents, "answer": answer}

    except Exception as e:
        logging.error(f"Error during answering question: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
                            
                            

