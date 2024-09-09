from fastapi import APIRouter, File, UploadFile, HTTPException, Depends, Form
from sqlalchemy.orm import Session
from src.pdf_processing import extract_text_from_pdf
from src.database.db import get_db
from src.entity.models import DocumentText, User
from src.services.auth import auth_service
import os

router = APIRouter(prefix="/pdf",tags=["PDF Upload"])


@router.post("/upload-pdf/")
async def upload_pdf(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):

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

        document = DocumentText(user_id=current_user.id,
                                filename=file.filename, text=text)
        db.add(document)
        db.commit()

        return {"message": "PDF processed and saved successfully", "text_sample": text[:2000]}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error processing PDF: {str(e)}")
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
