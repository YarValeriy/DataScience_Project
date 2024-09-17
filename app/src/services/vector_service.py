from transformers import AutoTokenizer, AutoModel
import torch
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import logging
from typing import List

# Load a pre-trained language model
tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")


# Convert PyTorch tensor to NumPy array, then to list
def vectorize_text_llm(text: str) -> list:
    try:
        logging.info(f"Vectorizing text: {text}")
        inputs = tokenizer(text, return_tensors='pt', padding=True, truncation=True)
        logging.info(f"Tokenized inputs: {inputs}")

        with torch.no_grad():
            embeddings = model(**inputs).last_hidden_state.mean(dim=1)

        vector_list = embeddings.tolist()
        logging.info(f"Generated vector list: {vector_list}")
        return vector_list
    except Exception as e:
        logging.error(f"Failed to vectorize text using LLM: {e}")
        raise ValueError(f"Failed to vectorize text using LLM: {e}")



# TF-IDF Vectorizer - Computed at runtime
def compute_tfidf(query: str, documents: list) -> np.ndarray:
    vectorizer = TfidfVectorizer()
    all_texts = [query] + documents  # Query + all document texts
    tfidf_matrix = vectorizer.fit_transform(all_texts)
    return tfidf_matrix


def compute_similarity(question: str, sentence: str) -> float:
    """
    Compute a more advanced similarity score between the question and a sentence using cosine similarity.

    Args:
        question (str): The question being asked.
        sentence (str): A sentence from the document.

    Returns:
        float: Similarity score.
    """
    vectorizer = TfidfVectorizer().fit_transform([question, sentence])
    vectors = vectorizer.toarray()
    cosine_sim = cosine_similarity([vectors[0]], [vectors[1]])[0][0]
    return cosine_sim

def extract_keywords(text: str, num_keywords: int = 10) -> List[str]:
    """
    Extract keywords from the text using TF-IDF.
    """
    vectorizer = TfidfVectorizer(stop_words='english', max_features=num_keywords)
    vectors = vectorizer.fit_transform([text])
    feature_names = vectorizer.get_feature_names_out()
    return feature_names.tolist()
