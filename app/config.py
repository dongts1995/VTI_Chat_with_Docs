"""Hằng số nghiệp vụ, lấy từ PRD và SAD."""

# US-201, CON-002: PDF tối đa 50 MB.
MAX_UPLOAD_BYTES = 50 * 1024 * 1024

# US-301: câu hỏi tối đa 2.000 ký tự.
MAX_QUESTION_CHARS = 2000

# SAD 2.2 bước 3, BR-006: dưới 20 ký tự mỗi trang coi như PDF không có chữ (file scan).
MIN_TEXT_CHARS_PER_PAGE = 20

# Số đoạn trích tối đa đưa vào một câu trả lời (US-302).
TOP_K_PASSAGES = 4

# Giới hạn độ dài một đoạn văn bản khi chia nhỏ (SAD 2.2 bước 5, rút gọn theo ký tự).
MAX_PASSAGE_CHARS = 500

# Số ký tự của đoạn trích hiển thị kèm trích dẫn.
EXCERPT_CHARS = 300
