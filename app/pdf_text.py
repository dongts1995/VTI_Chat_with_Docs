"""Trích xuất văn bản theo trang từ PDF (US-201, US-202, US-205)."""

import unicodedata
from io import BytesIO

from pypdf import PdfReader

from app.config import MIN_TEXT_CHARS_PER_PAGE
from app.errors import PdfError
from app.models import PageText


def extract_pages(data: bytes) -> list[PageText]:
    """Đọc toàn bộ trang của PDF; ném PdfError với lý do dễ hiểu nếu không đọc được."""
    try:
        reader = PdfReader(BytesIO(data))
        if reader.is_encrypted:
            raise PdfError("PASSWORD", "File PDF có mật khẩu. Hãy bỏ mật khẩu rồi tải lại.")
        return [
            PageText(number=number, text=unicodedata.normalize("NFC", page.extract_text() or ""))
            for number, page in enumerate(reader.pages, start=1)
        ]
    except PdfError:
        raise
    except Exception as exc:  # pypdf ném nhiều loại lỗi khác nhau với file hỏng
        raise PdfError("CORRUPT", "Không đọc được file PDF. File có thể bị hỏng.") from exc


def has_extractable_text(pages: list[PageText]) -> bool:
    """False khi PDF gần như không có chữ, tức là file scan (BR-006)."""
    total_chars = sum(len(page.text.strip()) for page in pages)
    return total_chars >= MIN_TEXT_CHARS_PER_PAGE * max(len(pages), 1)
