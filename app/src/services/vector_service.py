from transformers import AutoTokenizer, AutoModel
import torch
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import logging

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