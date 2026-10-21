"""Kho tài liệu trong bộ nhớ (ADR-0003: thay bằng PostgreSQL khi có hạ tầng)."""

import threading

from app.models import Document, DocumentStatus


class DocumentRepository:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._documents: dict[str, Document] = {}

    def add(self, document: Document) -> None:
        with self._lock:
            self._documents[document.id] = document

    def get(self, document_id: str) -> Document | None:
        with self._lock:
            return self._documents.get(document_id)

    def list_all(self) -> list[Document]:
        """Tài liệu theo thứ tự tải lên."""
        with self._lock:
            return list(self._documents.values())

    def list_ready(self) -> list[Document]:
        """Chỉ các tài liệu được phép dùng làm nguồn cho câu trả lời (US-202)."""
        return [d for d in self.list_all() if d.status is DocumentStatus.READY]
