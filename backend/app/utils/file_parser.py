"""
File parsers for PDF and DOCX resume files
"""

from typing import Optional
import io


def extract_text_from_pdf(file_content: bytes) -> str:
    """Extract text from PDF file"""
    try:
        import PyPDF2
        
        pdf_file = io.BytesIO(file_content)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        
        return text.strip()
        
    except Exception as e:
        print(f"PDF extraction error: {e}")
        return ""


def extract_text_from_docx(file_content: bytes) -> str:
    """Extract text from DOCX file"""
    try:
        import docx
        
        doc_file = io.BytesIO(file_content)
        doc = docx.Document(doc_file)
        
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        
        return text.strip()
        
    except Exception as e:
        print(f"DOCX extraction error: {e}")
        return ""


def extract_text_from_file(file_content: bytes, file_type: str) -> str:
    """Extract text based on file type"""
    
    if file_type == "application/pdf" or file_type.endswith(".pdf"):
        return extract_text_from_pdf(file_content)
    
    elif file_type in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/msword"] or file_type.endswith(".docx"):
        return extract_text_from_docx(file_content)
    
    elif file_type.startswith("text/"):
        # Plain text file
        return file_content.decode("utf-8", errors="ignore")
    
    else:
        raise ValueError(f"Unsupported file type: {file_type}")
