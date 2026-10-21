"""US-301 hỏi đáp, US-302 nhiều tài liệu, US-303 trích dẫn, US-304 không tìm thấy."""

import re

from fastapi.testclient import TestClient
from helpers import make_pdf
from httpx import Response

PRICE_LIST_PAGES = ["Bang gia dich vu. Gia thue van phong la 20 trieu dong moi thang."]
MEETING_ROOM_PAGES = ["Phong hop nang cao gom may chieu va bang trang."]


def _upload(client: TestClient, name: str, pages: list[str]) -> None:
    response = client.post(
        "/api/v1/documents", files={"file": (name, make_pdf(pages), "application/pdf")}
    )
    assert response.status_code == 201


def _ask(client: TestClient, text: str) -> dict:  # type: ignore[type-arg]
    response: Response = client.post("/api/v1/questions", json={"text": text})
    assert response.status_code == 200, response.text
    return response.json()  # type: ignore[no-any-return]


def test_question_is_answered_from_ready_document(client: TestClient) -> None:
    # US-301: câu hỏi tiếng Việt nhận câu trả lời có nội dung từ tài liệu.
    _upload(client, "hop_dong.pdf", ["Hop dong thue van phong. Thanh toan 30 phan tram khi ky."])

    answer = _ask(client, "Hợp đồng quy định thanh toán thế nào?")

    assert answer["status"] == "COMPLETED"
    assert "30 phan tram" in answer["text"]
    assert answer["readyDocCount"] == 1


def test_english_question_uses_same_index(client: TestClient) -> None:
    _upload(client, "contract.pdf", ["The payment term is 30 days after signing the contract."])

    answer = _ask(client, "What is the payment term?")

    assert answer["status"] == "COMPLETED"
    assert "payment term" in answer["text"]


def test_answer_combines_information_from_two_documents(client: TestClient) -> None:
    # US-302: thông tin nằm ở hai tài liệu khác nhau đều được trích.
    _upload(client, "bang_gia.pdf", PRICE_LIST_PAGES)
    _upload(client, "phong_hop.pdf", MEETING_ROOM_PAGES)

    answer = _ask(client, "Gia thue van phong va may chieu")

    file_names = {c["fileName"] for c in answer["citations"]}
    assert file_names == {"bang_gia.pdf", "phong_hop.pdf"}


def test_every_passage_has_a_numbered_citation_with_file_and_page(client: TestClient) -> None:
    # US-303: mỗi đoạn có [n]; trích dẫn ghi đúng tên tài liệu và số trang.
    _upload(client, "hop_dong.pdf", ["Trang mot. Thanh toan 30 phan tram khi ky ket."])
    _upload(client, "bang_gia.pdf", PRICE_LIST_PAGES)

    answer = _ask(client, "thanh toan thue van phong")

    lines = [line for line in answer["text"].splitlines() if line.strip()]
    citations = answer["citations"]
    assert len(lines) == len(citations) >= 1
    for index, (line, citation) in enumerate(zip(lines, citations, strict=True), start=1):
        assert line.endswith(f"[{index}]")
        assert citation["index"] == index
        assert citation["fileName"].endswith(".pdf")
        assert citation["page"] >= 1
        assert citation["excerpt"]
    cited_numbers = [int(n) for n in re.findall(r"\[(\d+)\]", answer["text"])]
    assert cited_numbers == list(range(1, len(citations) + 1))


def test_page_number_points_to_the_page_containing_the_answer(client: TestClient) -> None:
    _upload(
        client, "hop_dong.pdf", ["Trang mot khong lien quan.", "Thoi han thanh toan la 15 ngay."]
    )

    answer = _ask(client, "thoi han thanh toan")

    assert answer["citations"][0]["page"] == 2


def test_question_without_match_returns_not_found_with_document_count(client: TestClient) -> None:
    # US-304: không có thông tin thì báo rõ, kèm số tài liệu đã tìm.
    _upload(client, "hop_dong.pdf", ["Hop dong thue van phong."])
    _upload(client, "bang_gia.pdf", PRICE_LIST_PAGES)

    answer = _ask(client, "Lương nhân viên là bao nhiêu?")

    assert answer["status"] == "NOT_FOUND"
    assert answer["citations"] == []
    assert answer["text"].startswith("Không tìm thấy thông tin này trong 2 tài liệu hiện có.")
    assert answer["readyDocCount"] == 2


def test_scanned_document_is_never_used_as_a_source(client: TestClient) -> None:
    # US-205 + RUL: file NO_TEXT không xuất hiện trong trích dẫn.
    _upload(client, "scan.pdf", ["", ""])
    _upload(client, "bang_gia.pdf", PRICE_LIST_PAGES)

    answer = _ask(client, "gia thue van phong")

    assert {c["fileName"] for c in answer["citations"]} == {"bang_gia.pdf"}
    assert answer["readyDocCount"] == 1


def test_question_without_ready_document_is_a_conflict(client: TestClient) -> None:
    response = client.post("/api/v1/questions", json={"text": "bat ky cau hoi nao"})

    assert response.status_code == 409
    assert response.json()["code"] == "NO_READY_DOCUMENT"


def test_blank_question_is_rejected(client: TestClient) -> None:
    # US-301 AC4: khoảng trắng không được gửi đi.
    _upload(client, "bang_gia.pdf", PRICE_LIST_PAGES)

    response = client.post("/api/v1/questions", json={"text": "   "})

    assert response.status_code == 422
    assert response.json()["code"] == "EMPTY_QUESTION"


def test_question_over_2000_characters_is_rejected(client: TestClient) -> None:
    _upload(client, "bang_gia.pdf", PRICE_LIST_PAGES)

    response = client.post("/api/v1/questions", json={"text": "a" * 2001})

    assert response.status_code == 422
    assert response.json()["code"] == "QUESTION_TOO_LONG"


def test_question_of_exactly_2000_characters_is_accepted(client: TestClient) -> None:
    _upload(client, "bang_gia.pdf", PRICE_LIST_PAGES)

    response = client.post("/api/v1/questions", json={"text": "gia " * 500})

    assert response.status_code == 200
