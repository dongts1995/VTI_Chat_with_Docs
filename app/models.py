"""Mô hình miền: tài liệu, trang, đoạn văn và kết quả trả lời."""

from dataclasses import dataclass, field
from enum import StrEnum
from uuid import uuid4


class DocumentStatus(StrEnum):
    """Trạng thái xử lý tài liệu (US-202, US-205)."""

    READY = "READY"
    NO_TEXT = "NO_TEXT"
    ERROR = "ERROR"


class AnswerStatus(StrEnum):
    """Kết quả một lượt hỏi đáp (US-303, US-304)."""

    COMPLETED = "COMPLETED"
    NOT_FOUND = "NOT_FOUND"


@dataclass(frozen=True)
class PageText:
    number: int  # Số trang, bắt đầu từ 1.
    text: str


@dataclass
class Document:
    file_name: str
    status: DocumentStatus
    page_count: int = 0
    error: str | None = None
    pages: list[PageText] = field(default_factory=list)
    id: str = field(default_factory=lambda: str(uuid4()))


@dataclass(frozen=True)
class Passage:
    """Một đoạn văn nằm trong một trang của một tài liệu; dùng làm nguồn trích dẫn."""

    document_id: str
    file_name: str
    page: int
    text: str


@dataclass(frozen=True)
class Citation:
    index: int  # Số [n] xuất hiện trong câu trả lời.
    document_id: str
    file_name: str
    page: int
    excerpt: str


@dataclass(frozen=True)
class Answer:
    status: AnswerStatus
    text: str
    citations: list[Citation]
    ready_doc_count: int
