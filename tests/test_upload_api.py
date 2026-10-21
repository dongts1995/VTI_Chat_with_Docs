"""US-201 (tải PDF), US-202 (trạng thái và lý do lỗi), US-205 (PDF scan)."""

from fastapi.testclient import TestClient
from helpers import make_encrypted_pdf, make_pdf
from httpx import Response

from app.config import MAX_UPLOAD_BYTES


def _upload(
    client: TestClient, name: str, data: bytes, content_type: str = "application/pdf"
) -> Response:
    return client.post("/api/v1/documents", files={"file": (name, data, content_type)})


def test_pdf_upload_is_accepted_and_ready(client: TestClient) -> None:
    # US-201 AC1 + US-202: file hợp lệ vào kho ở trạng thái sẵn sàng.
    response = _upload(client, "hop_dong.pdf", make_pdf(["Hop dong thanh toan 30 phan tram."]))

    assert response.status_code == 201
    body = response.json()
    assert body["fileName"] == "hop_dong.pdf"
    assert body["pageCount"] == 1
    assert body["status"] == "READY"
    assert body["error"] is None


def test_uploaded_document_appears_in_list(client: TestClient) -> None:
    _upload(client, "a.pdf", make_pdf(["Noi dung mot."]))
    _upload(client, "b.pdf", make_pdf(["Noi dung hai.", "Trang hai."]))

    names = [d["fileName"] for d in client.get("/api/v1/documents").json()]
    assert names == ["a.pdf", "b.pdf"]


def test_non_pdf_extension_is_rejected(client: TestClient) -> None:
    # US-201 AC3: sai định dạng bị từ chối trước khi lưu.
    response = _upload(client, "ghi_chu.txt", b"%PDF-but-txt", "text/plain")

    assert response.status_code == 415
    assert response.headers["content-type"].startswith("application/problem+json")
    assert response.json()["code"] == "UNSUPPORTED_TYPE"
    assert client.get("/api/v1/documents").json() == []


def test_pdf_extension_without_pdf_signature_is_rejected(client: TestClient) -> None:
    response = _upload(client, "gia_mao.pdf", b"khong phai pdf")

    assert response.status_code == 415
    assert client.get("/api/v1/documents").json() == []


def test_file_over_50_mb_is_rejected_with_reason(client: TestClient) -> None:
    # US-201 AC3: vượt 50 MB bị từ chối với lý do rõ ràng.
    oversized = b"%PDF-" + b"0" * MAX_UPLOAD_BYTES

    response = _upload(client, "lon.pdf", oversized)

    assert response.status_code == 413
    assert response.json()["detail"] == "File vượt quá 50 MB."
    assert client.get("/api/v1/documents").json() == []


def test_scanned_pdf_is_flagged_no_text(client: TestClient) -> None:
    # US-205: PDF không có chữ được báo rõ, không dùng để trả lời.
    response = _upload(client, "scan.pdf", make_pdf(["", ""]))

    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "NO_TEXT"
    assert "scan" in body["error"]


def test_corrupt_pdf_is_flagged_error_with_reason(client: TestClient) -> None:
    # US-202 AC3: lỗi xử lý hiển thị lý do thường ngày.
    response = _upload(client, "hong.pdf", b"%PDF-1.4 noi dung hong khong doc duoc")

    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "ERROR"
    assert body["error"] == "Không đọc được file PDF. File có thể bị hỏng."


def test_password_protected_pdf_is_flagged_error(client: TestClient) -> None:
    response = _upload(client, "khoa.pdf", make_encrypted_pdf("secret"))

    body = response.json()
    assert body["status"] == "ERROR"
    assert "mật khẩu" in body["error"]


def test_home_page_and_health_are_served(client: TestClient) -> None:
    home = client.get("/")
    assert home.status_code == 200
    assert "Chat với tài liệu" in home.text
    assert client.get("/healthz").json() == {"status": "ok"}
