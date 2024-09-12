import fitz  # PyMuPDF library for handling PDFs
from fastapi import UploadFile
import nltk

async def process_pdf(file: UploadFile) -> str:
    """Extracts text from the uploaded PDF file asynchronously."""
    try:
        text = ""

        # Read the file content
        content = await file.read()  # Read the file asynchronously

        # Open the PDF using PyMuPDF
        with fitz.open(stream=content, filetype="pdf") as doc:
            for page in doc:
                text += page.get_text()
        # Remove newline characters
        cleaned_text = text.replace('\n', ' ')

        return cleaned_text

    except Exception as e:
        raise ValueError(f"Failed to process PDF: {e}")


