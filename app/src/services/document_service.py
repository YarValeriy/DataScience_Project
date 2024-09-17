from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException
from src.entity.models import Document
from src.services.summary_service import clean_text
from src.services.vector_service import vectorize_text_llm, compute_tfidf, compute_similarity
from src.repository.document_repository import get_documents_by_ids, get_all_documents, get_document_by_id
import numpy as np
import json
import logging
from typing import Tuple, List, Dict, Optional
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.tokenize import sent_tokenize

nltk.download('punkt')


# async def fetch_relevant_documents(query_text: str, search_scope: Optional[List[int]], db: AsyncSession):
#     """
#     Fetch relevant documents from the database based on a search query using both embeddings and TF-IDF.
#
#     Args:
#         query_text (str): The search query text.
#         search_scope(List[int]): list of document IDs
#         db (AsyncSession): The database session.
#
#     Returns:
#         List[Tuple[int, float]]: List of document IDs and their similarity scores.
#     """
#     # Vectorize the query text using LLM embeddings
#     cleaned_query = clean_text(query_text)
#     query_vector = vectorize_text_llm(cleaned_query)
#     query_vector = np.array(query_vector, dtype=float).flatten()
#
#     # Fetch all documents if search_scope is empty
#     try:
#         if not search_scope:
#             documents = await get_all_documents(db)
#         else:
#             documents = await get_documents_by_ids(search_scope, db)
#
#         document_texts = [doc.full_text for doc in documents if doc.full_text]
#         similarities = []
#
#         # Step 1: Compute TF-IDF scores
#         tfidf_matrix = compute_tfidf(cleaned_query, document_texts)
#         query_tfidf = tfidf_matrix[0]
#         document_tfidf_matrix = tfidf_matrix[1:]
#
#         tfidf_scores = cosine_similarity(query_tfidf, document_tfidf_matrix).flatten()
#
#         # Step 2: Compute Embedding similarity
#         for index, doc in enumerate(documents):
#             if doc.full_text_vector is None:
#                 continue
#
#             try:
#                 # Convert document vector to NumPy array
#                 doc_vector = np.array(json.loads(doc.full_text_vector), dtype=float).flatten()
#
#                 # Calculate embedding similarity
#                 embedding_similarity = np.dot(query_vector, doc_vector) / (
#                         np.linalg.norm(query_vector) * np.linalg.norm(doc_vector))
#
#                 # Combine TF-IDF and Embedding similarity
#                 combined_similarity = 0.5 * tfidf_scores[index] + 0.5 * embedding_similarity
#                 similarities.append((doc.document_id, combined_similarity))
#
#             except Exception as e:
#                 logging.error(f"Error processing document {doc.document_id}: {e}")
#                 continue
#
#         # Sort by combined similarity score
#         sorted_similarities = sorted(similarities, key=lambda x: x[1], reverse=True)
#         relevant_document_ids = [doc_id for doc_id, _ in sorted_similarities]
#         print(relevant_document_ids)
#         return relevant_document_ids
#
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to fetch relevant documents: {str(e)}")
#

async def search_document(query_text: str, db: AsyncSession) -> dict:
    """
    Fetch relevant documents based on the query vector using cosine similarity and TF-IDF.

    Args:
        query_text (str): The string representation of the query text.
        db (AsyncSession): The database session.

    Returns:
        Dict: Dictionary of document IDs and their similarity scores.
    """
    try:
        cleaned_query = clean_text(query_text)
        query_vector = vectorize_text_llm(cleaned_query)
        query_vector = np.array(query_vector, dtype=float).flatten()

        documents = await get_all_documents(db)
        document_texts = [doc.full_text for doc in documents if doc.full_text]
        similarities = []

        tfidf_matrix = compute_tfidf(cleaned_query, document_texts)
        query_tfidf = tfidf_matrix[0]
        document_tfidf_matrix = tfidf_matrix[1:]

        tfidf_scores = cosine_similarity(query_tfidf, document_tfidf_matrix).flatten()

        for index, doc in enumerate(documents):
            if doc.full_text_vector is None:
                continue

            try:
                doc_vector = np.array(json.loads(doc.full_text_vector), dtype=float).flatten()
                query_norm = np.linalg.norm(query_vector)
                doc_norm = np.linalg.norm(doc_vector)

                if query_norm != 0 and doc_norm != 0:
                    embedding_similarity = np.dot(query_vector, doc_vector) / (query_norm * doc_norm)
                    combined_similarity = 0.5 * tfidf_scores[index] + 0.5 * embedding_similarity
                    similarities.append((doc.document_id, combined_similarity))

            except Exception as e:
                logging.error(f"Error during document search: {e}")
                continue

        sorted_similarities = sorted(similarities, key=lambda x: x[1], reverse=True)
        return {"results": sorted_similarities}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


async def fetch_document_text(document_id: int, context_type: str, db: AsyncSession) -> str:
    """
    Fetch the document's full text or summary from the database.

    Args:
        document_id (int): The ID of the document.
        context_type (ContextType): Whether to fetch the full text or summary.
        db (AsyncSession): Database session.

    Returns:
        str: The document's text (full or summary).
    """
    try:
        # Query the document by its ID
        document = await get_document_by_id(document_id, db)

        if not document:
            raise ValueError(f"Document with ID {document_id} not found.")

        if context_type == "full_text":
            return document.full_text if document.full_text else ""
        elif context_type == "summary":
            return document.summary if document.summary else ""
        else:
            raise ValueError("Invalid context type. Must be FULL_TEXT or SUMMARY.")

    except Exception as e:
        raise ValueError(f"Error fetching document {document_id}: {e}")


async def retrieve_context_from_documents(question: str, filtered_documents: List[int], context_type: str, db: AsyncSession) -> str:
    """
    Retrieve the context from the relevant documents, ranking and selecting relevant passages.

    Args:
        question (str): The question being asked.
        filtered_documents (List[int]): List of relevant document IDs.
        context_type (str): FULL_TEXT or SUMMARY.
        db (AsyncSession): Database session.

    Returns:
        str: Concatenated relevant passages from documents.
    """
    document_passages = []

    for document_id in filtered_documents:
        # Fetch the full text or summary of the document from the database
        document_text = await fetch_document_text(document_id, context_type, db)

        if document_text:
            # Extract relevant passages from each document
            relevant_passages = extract_relevant_passage(document_text, question)
            # Calculate relevance score for each passage
            # seen_passages = set()
            for passage in relevant_passages:
                relevance_score = compute_similarity(question, passage)
                # if passage not in seen_passages and relevance_score > 0.1:  # Ensure relevance and uniqueness
                if relevance_score > 0.1:
                    # seen_passages.add(passage)
                    document_passages.append({"passage": passage, "relevance_score": relevance_score})

    # Ensure that passages are unique and relevant
    ranked_passages = sorted(document_passages, key=lambda x: x["relevance_score"], reverse=True)

    # Take only the top-ranked and diverse passages
    selected_passages = select_top_diverse_passages(ranked_passages, top_k=3)
    return " ".join(selected_passages)


def extract_relevant_passage(document_text: str, question: str) -> List[str]:
    """
    Split the document into smaller manageable chunks or passages for better context extraction.

    Args:
        document_text (str): The full text or summary of the document.
        question (str): The question being asked.

    Returns:
        List[str]: A list of passages from the document.
    """
    if not document_text:
        return []

    # Split the document into multiple sentences per chunk for better context
    sentences = sent_tokenize(document_text)
    passages = [" ".join(sentences[i:i+2]) for i in range(0, len(sentences), 2)]  # Adjust window size (2 sentences)

    return [p.strip() for p in passages if p.strip()]



def select_top_diverse_passages(ranked_passages: List[dict], top_k: int) -> List[str]:
    """
    Select top passages that are both relevant and diverse (i.e., not repeating the same content).

    Args:
        ranked_passages (List[dict]): Ranked list of passages.
        top_k (int): The number of passages to return.

    Returns:
        List[str]: A list of the top distinct passages.
    """
    selected_passages = []
    seen_passages = set()

    for passage_data in ranked_passages:
        passage = passage_data['passage']
        # Add passage if it hasn't been seen before
        if passage not in seen_passages:
            seen_passages.add(passage)
            selected_passages.append(passage)
        # Break if we have enough passages
        if len(selected_passages) >= top_k:
            break

    return selected_passages