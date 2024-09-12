from fastapi import APIRouter, File, UploadFile, HTTPException, Depends, Form
from sqlalchemy.orm import Session
from src.pdf_processing import extract_text_from_pdf
from src.database.db import get_db
from src.entity.models import DocumentText, User
from src.services.auth import auth_service
import os
from src.services.model import process_text


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





#############################################################################

### заглушка для роботи з LLM приймае і док-т і питання   вона відпрацювала добре, поки не використовую
# @router.post("/upload_new_pdf/")
# async def upload_new_pdf(
#     current_user: User = Depends(auth_service.get_current_user),
#     # request: Request,
#     text: str = Form(...),
#     # description: str = Form(...),
# ):

#     # ansver_text = process_text(text, description)
#     # return ansver_text
#     return None





### заглушка для завантаження ПДФ тексту в базу
@router.post("/upload_new_pdf_test/")
async def upload_new_pdf_test(
    current_user: User = Depends(auth_service.get_current_user),
    # request: Request,
    text: str = Form(...),         #передаю текст документу
    description: str = Form(...),  #передаю назва документу
):

    # тут функуія для збереження тексту документу і назви документу в базу
    
    return current_user         #то нічого не повертає






### заглушка для запиту назв доступних документів, в залежності від імені користувача
@router.post("/request_for_title_docs/")
async def request_for_title_docs(
    current_user: User = Depends(auth_service.get_current_user),
    # request: Request,
):
    
    # тут функція витягування завантажених в базі  назв документів

    name_documents = ["Документ1", "Документ2", "Документ3"]
    
    return name_documents  # Повертаємо список документів







### заглушка для запиту історії, залежно від документу і користувача
@router.post("/request_for_logs/")
async def request_for_logs(
    current_user: User = Depends(auth_service.get_current_user),
    # request: Request,
    document: str = Form(...), 
):
    documents_data = {
    "Документ1": [("Яке сьогодні число?", "Сьогодні 9 вересня."), ("Що на обід?", "На обід суп.")],
    "Документ2": [("Як тебе звати?", "Мене звати GPT."), ("Яка погода?", "Сонячно."), ("Скільки зараз часу?", "Зараз 12:00."), ("Який сьогодні день?", "Понеділок.")],
    "Документ3": [("Скільки зараз часу?", "Зараз 12:00."), ("Який сьогодні день?", "Понеділок.")]
    }

    document_content = documents_data.get(document, "") if document else ""
    # dialog_content = dialogs_data.get(name_documents, "") if name_documents else ""
    # функція, яка видягує історію запитів користувача по заданому документу

    return document_content








### заглушка для роботи з LLM по вибраному попереддньо документу.
@router.post("/ask_question/")
async def ask_question(
    current_user: User = Depends(auth_service.get_current_user),
    # request: Request,
    document: str = Form(...),
    question: str = Form(...),
):
    
    # тут функція, яка витягуе текст документу по його назві та в  залежності від користувача з бази даних

    text = "Мене звати Гена, мені 25 років, я самий красивий парень на селі, темні волоси, голубі очі, зріст 180 см."  # Типу витягнули текст

    ansver_text = process_text(text, question)
    # ansver = [(question, ansver_text),]

    # Тут іункція, яка додає запитання, відповідь в базу даних з логами користувача

    return ansver_text