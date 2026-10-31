import re
from PyPDF2 import PdfReader

class PDFExtractionError(Exception):
    """Custom exception raised when PDF text extraction fails or yields insufficient content."""
    pass

def extract_text_from_pdf(pdf_file) -> str:
    """
    Extracts, normalizes, and cleans text from an uploaded PDF file using PyPDF2.
    
    Args:
        pdf_file: An uploaded file object or file path.
        
    Returns:
        str: Cleaned and structured plain text extracted from the PDF.
        
    Raises:
        PDFExtractionError: If file is corrupted, unreadable, or contains no extractable text.
    """
    try:
        reader = PdfReader(pdf_file)
        if len(reader.pages) == 0:
            raise PDFExtractionError("The uploaded PDF file has no pages.")
        
        extracted_pages = []
        for index, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            if text.strip():
                extracted_pages.append(text.strip())
        
        full_text = "\n\n".join(extracted_pages)
        
        # Normalize whitespace and strange line breaks
        cleaned_text = re.sub(r'[ \t]+', ' ', full_text)
        cleaned_text = re.sub(r'\n{3,}', '\n\n', cleaned_text).strip()
        
        if len(cleaned_text) < 50:
            raise PDFExtractionError(
                "Unable to extract readable text from this PDF. It may be an image-only scan or password-protected. "
                "Please upload a standard text PDF resume or load our sample profile."
            )
            
        return cleaned_text
        
    except PDFExtractionError:
        raise
    except Exception as e:
        raise PDFExtractionError(f"Error reading PDF file: {str(e)}")
