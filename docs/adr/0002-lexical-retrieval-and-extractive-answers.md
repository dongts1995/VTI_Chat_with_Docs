# ADR-0002: Truy xuất BM25 và câu trả lời trích xuất, chưa dùng LLM hay embedding

- **Trạng thái:** Accepted (MVP); thay thế một phần ADR-07, ADR-08, ADR-09 của SAD
- **Ngày:** 2026-10-21

## Bối cảnh
SAD chọn truy xuất lai (vector 1024 chiều + full-text) và LLM Claude qua port `AnswerGenerator`. Trong môi trường hiện tại chưa có API key LLM và chưa có model embedding BGE-M3 chạy được. Yêu cầu US-303 (mỗi ý có trích dẫn) và US-304 (không bịa thông tin) cần được kiểm chứng ngay bằng test tự động.

## Quyết định
1. **Truy xuất:** BM25 trên từ khoá đã bỏ dấu tiếng Việt (`app/retrieval.py`). Không dùng embedding.
2. **Sinh câu trả lời:** `ExtractiveAnswerGenerator` lấy tối đa 2 câu có từ khoá trùng với câu hỏi từ mỗi đoạn, và gắn `[n]`. Không gọi LLM.
3. **Port giữ nguyên:** `AnswerGenerator` là `Protocol`. Khi có khoá LLM, lớp mới cài đặt port này; `QuestionService` không đổi.
4. **Giới hạn đã biết:** câu hỏi tiếng Anh chỉ khớp với tài liệu tiếng Anh; câu hỏi tiếng Việt chỉ khớp với tài liệu tiếng Việt. Không có hiểu ngữ nghĩa, nên diễn đạt khác từ khoá có thể bị "không tìm thấy" (ảnh hưởng M-002).

## Hệ quả
- Kết quả xác định, kiểm thử được, không tốn chi phí API.
- Chất lượng tổng hợp đa tài liệu thấp hơn LLM. Đây là rủi ro chính cần đo bằng bộ 15 câu hỏi (US-302 AC) trước khi nghiệm thu.
- Với mỗi lần hỏi, toàn bộ chỉ mục được dựng lại từ mọi tài liệu READY. Chấp nhận được ở vài chục tài liệu; cần cache chỉ mục khi tăng lên 500 tài liệu (SAD NFR-06).

**Why:** tách nghiệp vụ (chọn đoạn, gắn trích dẫn, báo không tìm thấy) khỏi nhà cung cấp mô hình, để nghiệp vụ được test không cần mạng.
**How to apply:** khi cài LLM, giữ nguyên bước truy xuất và kiểm tra trích dẫn; chạy lại `tests/test_qa_api.py` để chứng minh không hồi quy.
