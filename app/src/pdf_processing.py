import pdfplumber


def extract_text_from_pdf(pdf_path: str) -> str:

    text = ''
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                cleaned_text = page_text.replace('\n', ' ')
                text += cleaned_text
    return text
