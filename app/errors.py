"""Lỗi nghiệp vụ, được API trả về theo RFC 9457 (problem+json)."""


class AppError(Exception):
    """Lỗi có thể hiển thị cho người dùng bằng tiếng Việt thường ngày."""

    def __init__(self, status_code: int, code: str, message: str) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.message = message


class PdfError(Exception):
    """Không đọc được PDF; `message` là lý do hiển thị cho người dùng (US-202)."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
