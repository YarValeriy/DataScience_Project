from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
from typing import Tuple, List, Dict
import torch
from src.services.vector_service import vectorize_text_llm, extract_keywords
import re
import string
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from src.entity.models import Document

nltk.download('stopwords')
nltk.download('punkt')

# Initialize the summarizer and tokenizer pipeline with mBART for multilingual support
tokenizer = AutoTokenizer.from_pretrained("facebook/mbart-large-50")
model = AutoModelForSeq2SeqLM.from_pretrained("facebook/mbart-large-50")
summarizer = pipeline("summarization", model=model, tokenizer=tokenizer)
# tokenizer = AutoTokenizer.from_pretrained("facebook/bart-large-cnn")
# model = AutoModelForSeq2SeqLM.from_pretrained("facebook/bart-large-cnn")


def generate_summary(cleaned_text: str, src_lang: str = "uk", max_length: int = 30, min_length: int = 10) -> Tuple[str, List[float]]:
    """Generates a summary and its corresponding vector representation.

    Args:
        cleaned_text (str): The input full text to summarize.
        src_lang (str): The source language code for the summarization model.
        max_length (int): Maximum length of the summary for each chunk.
        min_length (int): Minimum length of the summary for each chunk.

    Returns:
        Tuple[str, List[float]]: A tuple containing the full summary and its vector.
    """
    try:
        # Handle short or empty text
        if not cleaned_text.strip():
            raise ValueError("The input text is empty or only contains whitespace.")

        # Define the maximum length for chunks
        max_chunk_length = 1024

        # Split text into manageable chunks
        chunks = [cleaned_text[i:i + max_chunk_length] for i in range(0, len(cleaned_text), max_chunk_length)]

        # Generate summaries for each chunk
        summaries = []
        for chunk in chunks:
            # Use mBART with the appropriate language code
            forced_bos_token_id = tokenizer.lang_code_to_id.get(f"{src_lang}_XX", None)

            summarized_chunk = summarizer(
                chunk,
                max_length=max_length,  # Dynamic length
                min_length=min_length,   # Dynamic length
                do_sample=False,
                forced_bos_token_id=forced_bos_token_id
            )[0]['summary_text']
            summaries.append(summarized_chunk)

        # Combine all summaries into one
        full_summary = " ".join(summaries)
        full_summary = post_process_summary(full_summary)


        return full_summary

    except Exception as e:
        raise ValueError(f"Failed to generate summary: {e}")


def post_process_summary(summary: str) -> str:
    """
    Cleans up redundant or irrelevant information from the summary.
    """
    # Remove extra spaces, numbers, and repetitive phrases
    processed_summary = re.sub(r'\s+', ' ', summary)  # Remove extra spaces
    processed_summary = re.sub(r'\b\d+\b', '', processed_summary)  # Remove numbers
    return processed_summary.strip()


def clean_text(text: str, lang: str = "en") -> str:
    """Cleans the input text by removing punctuation, stop words, and normalizing case.

    Args:
        text (str): The text to clean.
        lang (str): The language of the stop words to use (default is English).

    Returns:
        str: The cleaned text.
    """
    # Convert text to lowercase
    text = text.lower()

    # Remove punctuation
    text = re.sub(f"[{re.escape(string.punctuation)}]", "", text)

    # Tokenize the text
    words = word_tokenize(text)

    # Remove stop words
    if lang in stopwords.fileids():
        stop_words = set(stopwords.words(lang))
    else:
        stop_words = set()  # Default to empty set if language not supported

    cleaned_text = " ".join(word for word in words if word not in stop_words)

    return cleaned_text


def generate_answer_based_on_context(question: str, context_text: str) -> str:
    """
    Generate an answer based on the provided context with post-processing.

    Args:
        question (str): The question to be answered.
        context_text (str): The concatenated context string.

    Returns:
        str: Generated answer.
    """
    # Check if context_text is provided
    if not context_text:
        return "No relevant context found to answer the question."

    try:
        # Combine question and context
        input_text = f"question: {question} context: {context_text}"

        # Tokenize input
        inputs = tokenizer.encode(input_text, return_tensors="pt", max_length=1024, truncation=True)

        # Generate the answer with constraints
        outputs = model.generate(
            inputs,
            max_length=150,
            num_return_sequences=1,
            repetition_penalty=2.0,  # Reduce redundancy
            num_beams=4              # Improve diversity
        )

        # Decode the output to get the answer in text form
        answer = tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Post-process answer: remove boilerplate and irrelevant sentences
        processed_answer = post_process_answer(answer)

        return processed_answer

    except Exception as e:
        raise ValueError(f"Failed to generate answer: {e}")

def post_process_answer(answer: str) -> str:
    """
    Refine the generated answer by removing irrelevant parts.

    Args:
        answer (str): The raw generated answer.

    Returns:
        str: Processed answer.
    """
    # Simple post-processing: remove non-informative or redundant text
    sentences = answer.split(". ")
    important_sentences = [sent for sent in sentences if is_informative(sent)]
    return ". ".join(important_sentences)

def is_informative(sentence: str) -> bool:
    """
    Determine if a sentence is informative or just filler.

    Args:
        sentence (str): A sentence to evaluate.

    Returns:
        bool: True if the sentence is relevant, False otherwise.
    """
    filler_phrases = ["In conclusion", "As mentioned", "To summarize"]
    return not any(phrase in sentence for phrase in filler_phrases)


def generate_summary_with_keywords(cleaned_text: str, keywords: List[str], max_length: int = 100, min_length: int = 30) -> str:
    """
    Generates summaries for each text chunk, emphasizing important keywords.
    """
    max_chunk_length = 1024
    chunks = [cleaned_text[i:i + max_chunk_length] for i in range(0, len(cleaned_text), max_chunk_length)]

    summaries = []
    for chunk in chunks:
        # Include keywords to guide the summarization process
        keyword_str = " ".join(keywords)
        prompt = f"{chunk} Keywords: {keyword_str}"

        # Use mBART to summarize with forced language token
        forced_bos_token_id = tokenizer.lang_code_to_id.get(f"uk_XX", None)
        summarized_chunk = summarizer(
            prompt,
            max_length=max_length,
            min_length=min_length,
            do_sample=False,
            forced_bos_token_id=forced_bos_token_id
        )[0]['summary_text']

        summaries.append(summarized_chunk)

    # Combine the summaries into one
    full_summary = " ".join(summaries)
    return full_summary


def post_process_summary_kw(summary: str, keywords: List[str], original_text: str) -> str:
    """
    Ensures the generated summary includes the most important keywords.
    """
    missing_keywords = [keyword for keyword in keywords if keyword not in summary]

    if missing_keywords:
        # Add relevant sentences from the original text to cover missing keywords
        for keyword in missing_keywords:
            keyword_sentence = next((sentence for sentence in original_text.split('. ') if keyword in sentence), "")
            if keyword_sentence:
                summary += f" {keyword_sentence}."

    return summary




