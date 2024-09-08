from transformers import pipeline, AutoTokenizer, AutoModelForQuestionAnswering
import torch

# Завантажуємо модель один раз при старті
model_name = "timpal0l/mdeberta-v3-base-squad2"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForQuestionAnswering.from_pretrained(model_name)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)

# Створюємо pipeline для обробки
qa_model = pipeline("question-answering", model=model, tokenizer=tokenizer, device=device)



def process_text(text: str, question: str):
    # Використовуємо модель для обробки тексту
    model_name = "timpal0l/mdeberta-v3-base-squad2"
    qa_pipeline = pipeline("question-answering", model=model_name, device=device)
    
    # Приклад питання для моделі
    # question = "Яка мета була у чеховського натуралізму?"
    
    # Обробка тексту (контекст) з використанням питання
    result = qa_pipeline(question=question, context=text)
    
    return result['answer']
