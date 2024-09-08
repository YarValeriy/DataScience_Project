from fastapi import APIRouter, File, UploadFile, HTTPException
from src.pdf_processing import extract_text_from_pdf
from src.services.auth import auth_service
from src.services.model import process_text
from src.entity.models import User
from fastapi import APIRouter, Form, HTTPException, Depends
import os

router = APIRouter(prefix="/pdf",tags=["PDF Upload"])


@router.post("/upload-pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=400, detail="Only PDF files are allowed")

    content = await file.read()
    temp_file_path = f"temp_{file.filename}"
    with open(temp_file_path, 'wb') as f:
        f.write(content)

    try:
        text = extract_text_from_pdf(temp_file_path)
        if not text:
            raise ValueError(
                "Extracted text is empty. Please check the PDF content.")

        return {
            "message": "PDF processed successfully",
            "text_sample": text[:2000]
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error processing PDF: {str(e)}")
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)



@router.post("/upload_new_pdf/")
async def echo_text(
    current_user: User = Depends(auth_service.get_current_user),
    # request: Request,
    text: str = Form(...),
    description: str = Form(...),
):

    answer_text = process_text(text, description)
    return answer_text