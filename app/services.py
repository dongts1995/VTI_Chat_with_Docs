"""Nghiệp vụ: tải và xử lý tài liệu (E2), hỏi đáp có trích dẫn (E3)."""

from app.answering import AnswerGenerator
from app.chunking import passages_of
from app.config import EXCERPT_CHARS, MAX_QUESTION_CHARS, MAX_UPLOAD_BYTES, TOP_K_PASSAGES
from app.errors import AppError, PdfError
from app.models import Answer, AnswerStatus, Citation, Document, DocumentStatus
from app.pdf_text import extract_pages, has_extractable_text
from app.repository import DocumentRepository
from app.retrieval import PassageIndex


class DocumentService:
    def __init__(self, repository: DocumentRepository) -> None:
        self._repository = repository

    def upload(self, file_name: str, data: bytes) -> Document:
        """Kiểm tra file, trích xuất văn bản và lưu tài liệu (US-201).

        Xử lý đồng bộ trong MVP; lỗi đọc PDF không làm mất bản ghi mà đặt trạng thái ERROR (US-202).
        """
        if len(data) > MAX_UPLOAD_BYTES:
            raise AppError(413, "FILE_TOO_LARGE", "File vượt quá 50 MB.")
        if not file_name.lower().endswith(".pdf") or not data.startswith(b"%PDF-"):
            raise AppError(415, "UNSUPPORTED_TYPE", "Chỉ chấp nhận file PDF.")

        document = Document(file_name=file_name, status=DocumentStatus.READY)
        try:
            pages = extract_pages(data)
        except PdfError as exc:
            document.status = DocumentStatus.ERROR
            document.error = exc.message
        else:
            document.page_count = len(pages)
            document.pages = pages
            if not has_extractable_text(pages):
                document.status = DocumentStatus.NO_TEXT
                document.error = "File không có chữ đọc được (có thể là bản scan)."
        self._repository.add(document)
        return document

    def list_documents(self) -> list[Document]:
        return self._repository.list_all()


class QuestionService:
    def __init__(self, repository: DocumentRepository, generator: AnswerGenerator) -> None:
        self._repository = repository
        self._generator = generator

    def ask(self, question: str) -> Answer:
        """Trả lời câu hỏi từ các tài liệu READY; không có nguồn phù hợp thì NOT_FOUND (US-304)."""
        text = question.strip()
        if not text:
            raise AppError(422, "EMPTY_QUESTION", "Câu hỏi không được để trống.")
        if len(text) > MAX_QUESTION_CHARS:
            raise AppError(422, "QUESTION_TOO_LONG", "Câu hỏi vượt quá 2.000 ký tự.")

        ready = self._repository.list_ready()
        if not ready:
            raise AppError(
                409,
                "NO_READY_DOCUMENT",
                "Chưa có tài liệu nào sẵn sàng. Hãy tải tài liệu lên trước.",
            )

        index = PassageIndex(passage for document in ready for passage in passages_of(document))
        hits = index.search(text, TOP_K_PASSAGES)
        if not hits:
            return Answer(
                status=AnswerStatus.NOT_FOUND,
                text=(
                    f"Không tìm thấy thông tin này trong {len(ready)} tài liệu hiện có. "
                    "Hãy thử diễn đạt lại câu hỏi hoặc tải thêm tài liệu."
                ),
                citations=[],
                ready_doc_count=len(ready),
            )

        citations = [
            Citation(
                index=i,
                document_id=passage.document_id,
                file_name=passage.file_name,
                page=passage.page,
                excerpt=passage.text[:EXCERPT_CHARS],
            )
            for i, passage in enumerate(hits, start=1)
        ]
        return Answer(
            status=AnswerStatus.COMPLETED,
            text=self._generator.generate(text, hits),
            citations=citations,
            ready_doc_count=len(ready),
        )
