import PyPDF2
from docx import Document
import os
import base64
def read_text_file(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    else:
        return "File not found."

def extract_text_from_pdf(file_path):
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text

def extract_text_from_docx(file_path):
    doc = Document(file_path)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text

def save_uploaded_file(contents, filename, upload_dir):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)

    upload_path = os.path.join(upload_dir, filename)
    with open(upload_path, 'wb') as f:
        f.write(decoded)

    return upload_path

def process_uploaded_file(file_path):
    if file_path.endswith('.txt'):
        return read_text_file(file_path)
    elif file_path.endswith('.pdf'):
        return extract_text_from_pdf(file_path)
    elif file_path.endswith('.docx'):
        return extract_text_from_docx(file_path)
    else:
        return "Unsupported file format."

def convert_to_txt(file_path, upload_dir):
    if file_path.endswith('.pdf'):
        text = extract_text_from_pdf(file_path)
    elif file_path.endswith('.docx'):
        text = extract_text_from_docx(file_path)
    elif file_path.endswith('.txt'):
        return file_path
    else:
        return None

    txt_filename = os.path.splitext(os.path.basename(file_path))[0] + '.txt'
    txt_file_path = os.path.join(upload_dir, txt_filename)

    with open(txt_file_path, 'w', encoding='utf-8') as txt_file:
        txt_file.write(text)
    if os.path.exists(file_path):
        os.remove(file_path)

    return txt_file_path