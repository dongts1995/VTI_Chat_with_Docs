"""Điểm vào API. Chạy: `uvicorn app.main:app` (xem README)."""

from pathlib import Path

from fastapi import FastAPI, Request, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

from app.answering import AnswerGenerator, ExtractiveAnswerGenerator
from app.config import MAX_UPLOAD_BYTES
from app.errors import AppError
from app.models import Answer, Document
from app.repository import DocumentRepository
from app.services import DocumentService, QuestionService

_STATIC_DIR = Path(__file__).parent / "static"


class _Out(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class DocumentOut(_Out):
    id: str
    file_name: str
    page_count: int
    status: str
    error: str | None


class CitationOut(_Out):
    index: int
    document_id: str
    file_name: str
    page: int
    excerpt: str


class AnswerOut(_Out):
    status: str
    text: str
    citations: list[CitationOut]
    ready_doc_count: int


class QuestionIn(BaseModel):
    text: str


def _document_out(document: Document) -> DocumentOut:
    return DocumentOut(
        id=document.id,
        file_name=document.file_name,
        page_count=document.page_count,
        status=document.status.value,
        error=document.error,
    )


def _answer_out(answer: Answer) -> AnswerOut:
    return AnswerOut(
        status=answer.status.value,
        text=answer.text,
        citations=[
            CitationOut(
                index=c.index,
                document_id=c.document_id,
                file_name=c.file_name,
                page=c.page,
                excerpt=c.excerpt,
            )
            for c in answer.citations
        ],
        ready_doc_count=answer.ready_doc_count,
    )


def create_app(
    repository: DocumentRepository | None = None,
    generator: AnswerGenerator | None = None,
) -> FastAPI:
    repo = repository or DocumentRepository()
    documents = DocumentService(repo)
    questions = QuestionService(repo, generator or ExtractiveAnswerGenerator())

    app = FastAPI(title="Chat với tài liệu (MVP)", version="0.1.0")

    @app.exception_handler(AppError)
    async def _app_error(_request: Request, exc: AppError) -> JSONResponse:
        # RFC 9457: application/problem+json (SAD 2.4).
        body = {
            "type": f"about:blank#{exc.code}",
            "title": exc.code,
            "status": exc.status_code,
            "code": exc.code,
            "detail": exc.message,
        }
        return JSONResponse(
            body, status_code=exc.status_code, media_type="application/problem+json"
        )

    @app.get("/healthz")
    def healthz() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/api/v1/documents", response_model=list[DocumentOut])
    def list_documents() -> list[DocumentOut]:
        return [_document_out(d) for d in documents.list_documents()]

    @app.post("/api/v1/documents", response_model=DocumentOut, status_code=201)
    async def upload_document(file: UploadFile) -> DocumentOut:
        # Đọc có giới hạn để file quá lớn không chiếm hết bộ nhớ; service kiểm tra lại.
        data = await file.read(MAX_UPLOAD_BYTES + 1)
        document = documents.upload(file.filename or "", data)
        return _document_out(document)

    @app.post("/api/v1/questions", response_model=AnswerOut)
    def ask_question(body: QuestionIn) -> AnswerOut:
        return _answer_out(questions.ask(body.text))

    @app.get("/", include_in_schema=False)
    def index() -> FileResponse:
        return FileResponse(_STATIC_DIR / "index.html")

    app.mount("/static", StaticFiles(directory=_STATIC_DIR), name="static")
    return app


app = create_app()
