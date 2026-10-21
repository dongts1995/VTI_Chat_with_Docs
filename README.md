# Chat với tài liệu (MVP)

Tải file PDF lên kho chung, hỏi bằng tiếng Việt hoặc tiếng Anh, nhận câu trả lời có trích dẫn tên tài liệu và số trang.

```bash
python -m venv .venv && .venv\Scripts\activate    # Windows (Linux/macOS: source .venv/bin/activate)
pip install -e ".[dev]"
uvicorn app.main:app --reload                      # mở http://127.0.0.1:8000
pytest                                             # test, yêu cầu coverage ≥ 70%
```

Không cần cấu hình thêm cho MVP. Dữ liệu nằm trong bộ nhớ và mất khi dừng server.

## Phạm vi MVP
Hai user story xương sống (xem `docs/02-requirements/PRD.md`):
- **US-201**: tải PDF ≤ 50 MB; **US-202 / US-205**: trạng thái và lý do lỗi, nhận diện PDF scan.
- **US-301 → US-304**: hỏi đáp có trích dẫn `[n]`, tổng hợp nhiều tài liệu, báo "không tìm thấy".

Chưa có trong MVP: đăng nhập (US-101→103), xoá tài liệu, streaming, phản hồi 👍/👎. Chi tiết và lý do: [docs/adr/0001-mvp-scope.md](docs/adr/0001-mvp-scope.md). Ma trận truy vết: [docs/traceability.md](docs/traceability.md).

## Tài liệu
- Đặc tả và thiết kế: [docs/](docs/) (BRD, PRD, SAD, Blueprint, use case).
- Hướng dẫn cho agent và quy ước: [AGENTS.md](AGENTS.md).
- Quyết định kiến trúc: [docs/adr/](docs/adr/).
