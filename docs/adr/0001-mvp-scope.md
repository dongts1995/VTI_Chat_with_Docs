# ADR-0001: Phạm vi MVP và các lệch so với SAD

- **Trạng thái:** Accepted (MVP)
- **Ngày:** 2026-10-21
- **Liên quan:** PRD §3, SAD ADR-01 → ADR-12

## Bối cảnh
SAD đề xuất một kiến trúc đầy đủ (OIDC, PostgreSQL + pgvector, worker, SSE, BGE-M3, LLM). Slide Day 5 yêu cầu chốt **2 user story xương sống** và có MVP chạy được, có test, có CI trong một buổi.

## Quyết định
1. **Phạm vi:** chỉ làm US-201 (tải PDF), US-202/205 (trạng thái, PDF scan) và US-301→304 (hỏi đáp có trích dẫn, không tìm thấy).
2. **Hoãn:** đăng nhập và phân quyền (US-101→103), xoá tài liệu (US-204), trùng lặp (US-206), streaming (US-306/310), hội thoại nhiều lượt (US-308/311), phản hồi và số liệu (US-309, US-401/402).
3. **Python 3.11+** thay vì 3.12 như ADR-02: môi trường phát triển hiện tại chỉ có 3.11; mã không dùng tính năng riêng của 3.12. Nâng lên 3.12 khi CI và máy dev đã sẵn sàng.

## Hệ quả
- Mọi lệch khác so với SAD được ghi trong ADR-0002 và ADR-0003.
- Các mục hoãn có trạng thái "Chưa làm" trong [docs/traceability.md](../traceability.md), không ẩn đi.
- Khi thêm story mới, cập nhật ma trận truy vết trong cùng PR.

**Why:** đội nhỏ, chưa chốt nơi vận hành (OQ-008), và slide yêu cầu bằng chứng chạy được hơn là đủ tính năng.
**How to apply:** trước khi thêm tính năng ngoài hai story trên, mở ADR mới và đối chiếu với SAD.
