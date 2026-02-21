"""
Service: File Parser
Converts .txt, .docx uploads and pasted text into clean plain text.
"""
import io
from typing import Optional


def parse_uploaded_file(file_obj, filename: str) -> tuple[str, str]:
    """
    Parse a Streamlit UploadedFile object.
    Returns (clean_text, detected_input_type).
    Raises ValueError on unsupported format.
    """
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    if ext == "txt":
        raw_bytes = file_obj.read()
        text = raw_bytes.decode("utf-8", errors="ignore")
        return _clean(text), "upload_txt"

    elif ext == "docx":
        try:
            import mammoth
            file_obj.seek(0)
            result = mammoth.extract_raw_text(file_obj)
            return _clean(result.value), "upload_docx"
        except ImportError:
            # Fallback: try python-docx
            import docx
            file_obj.seek(0)
            doc = docx.Document(file_obj)
            text = "\n".join(para.text for para in doc.paragraphs)
            return _clean(text), "upload_docx"

    else:
        raise ValueError(f"Unsupported file type '.{ext}'. Please upload .txt or .docx only.")


def parse_pasted_text(text: str) -> tuple[str, str]:
    """Clean and validate pasted text input."""
    if not text or not text.strip():
        raise ValueError("Pasted text is empty. Please provide content.")
    return _clean(text), "paste"


def _clean(text: str) -> str:
    """Normalize whitespace and strip injection-like patterns."""
    import re
    # Normalize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Remove excessive blank lines
    text = re.sub(r'\n{3,}', '\n\n', text)
    # Remove excessive spaces
    text = re.sub(r'[ \t]{2,}', ' ', text)
    # Basic prompt injection protection
    INJECTION_PATTERNS = [
        r'ignore (all )?previous instructions',
        r'you are now',
        r'act as a',
        r'disregard (all )?prior',
        r'\[SYSTEM\]',
    ]
    for pattern in INJECTION_PATTERNS:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    return text.strip()[:100_000]  # Hard cap at 100K chars (~50 pages)


def validate_file_size(file_obj, max_mb: int = 50) -> bool:
    """Returns True if file is within size limit."""
    file_obj.seek(0, 2)  # Seek to end
    size_bytes = file_obj.tell()
    file_obj.seek(0)     # Reset
    return size_bytes <= max_mb * 1024 * 1024
