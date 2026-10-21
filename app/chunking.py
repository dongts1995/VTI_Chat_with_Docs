"""Chia văn bản từng trang thành đoạn ngắn; đoạn không vượt qua ranh giới trang (SAD 2.2)."""

import re

from app.config import MAX_PASSAGE_CHARS
from app.models import Document, Passage

_SENTENCE_BREAK = re.compile(r"(?<=[.!?])\s+|\n{2,}")


def split_text(text: str, max_chars: int = MAX_PASSAGE_CHARS) -> list[str]:
    """Gộp câu thành đoạn, mỗi đoạn tối đa `max_chars` ký tự (một câu quá dài vẫn giữ nguyên)."""
    segments: list[str] = []
    current = ""
    for raw in _SENTENCE_BREAK.split(text):
        sentence = " ".join(raw.split())
        if not sentence:
            continue
        if current and len(current) + len(sentence) + 1 > max_chars:
            segments.append(current)
            current = sentence
        else:
            current = f"{current} {sentence}".strip()
    if current:
        segments.append(current)
    return segments


def passages_of(document: Document) -> list[Passage]:
    """Tất cả đoạn của một tài liệu, mỗi đoạn gắn với đúng số trang của nó."""
    return [
        Passage(
            document_id=document.id,
            file_name=document.file_name,
            page=page.number,
            text=segment,
        )
        for page in document.pages
        for segment in split_text(page.text)
    ]
