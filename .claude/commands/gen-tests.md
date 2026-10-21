---
description: Sinh test từ AC của một user story (không mock phần lõi)
argument-hint: <US-nnn>
---

Viết test tự động cho các AC của $ARGUMENTS:

1. Mỗi AC ứng với ít nhất một test, đặt tên hoặc comment có mã US và AC.
2. Dùng PDF thật từ `tests/helpers.py` (`make_pdf`), không mock `DocumentService`, `QuestionService` hay bộ truy xuất.
3. Với mỗi AC có điều kiện biên (ranh giới 50 MB, 2.000 ký tự, PDF scan), viết test cho cả hai phía của ranh giới.
4. Chạy `pytest`; mọi test mới phải pass. Không đổi test cũ để cho pass.
5. Cập nhật trạng thái trong `docs/traceability.md`.
