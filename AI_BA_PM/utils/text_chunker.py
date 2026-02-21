"""
Utility: Token-aware text chunker.
Splits long input text into chunks that fit within the AI context window.
"""
import re

try:
    import tiktoken
    _enc = tiktoken.get_encoding("cl100k_base")
    def _count_tokens(text: str) -> int:
        return len(_enc.encode(text))
except Exception:
    # Fallback: rough estimate (1 token ≈ 4 characters)
    def _count_tokens(text: str) -> int:
        return len(text) // 4


def chunk_text(text: str, max_tokens: int = 4000) -> list[str]:
    """
    Split text into chunks of at most `max_tokens` tokens.
    Tries to split on paragraph boundaries first, then sentence boundaries.
    Returns a list of chunk strings (at least one element).
    """
    text = text.strip()
    if not text:
        return [""]

    total_tokens = _count_tokens(text)
    if total_tokens <= max_tokens:
        return [text]

    # Try splitting on double newlines (paragraphs)
    paragraphs = re.split(r'\n\s*\n', text)
    chunks: list[str] = []
    current = ""

    for para in paragraphs:
        candidate = (current + "\n\n" + para).strip() if current else para
        if _count_tokens(candidate) <= max_tokens:
            current = candidate
        else:
            if current:
                chunks.append(current)
            # If single paragraph is too big, split on sentences
            if _count_tokens(para) > max_tokens:
                chunks.extend(_split_by_sentence(para, max_tokens))
                current = ""
            else:
                current = para

    if current:
        chunks.append(current)

    return chunks if chunks else [text[:max_tokens * 4]]


def _split_by_sentence(text: str, max_tokens: int) -> list[str]:
    """Fallback: split on sentence boundaries."""
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks: list[str] = []
    current = ""
    for sentence in sentences:
        candidate = (current + " " + sentence).strip() if current else sentence
        if _count_tokens(candidate) <= max_tokens:
            current = candidate
        else:
            if current:
                chunks.append(current)
            current = sentence[:max_tokens * 4]  # Hard truncate as last resort
    if current:
        chunks.append(current)
    return chunks


def get_token_count(text: str) -> int:
    return _count_tokens(text)
