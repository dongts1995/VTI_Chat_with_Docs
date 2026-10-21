# ADR-0003: Kho tài liệu trong bộ nhớ và xử lý PDF đồng bộ

- **Trạng thái:** Accepted (MVP); thay thế ADR-04 và ADR-05 của SAD ở giai đoạn này
- **Ngày:** 2026-10-21

## Bối cảnh
SAD yêu cầu PostgreSQL 16 + pgvector, hàng đợi job trong PostgreSQL và worker riêng, để tài liệu xử lý bất đồng bộ trong tối đa 5 phút (NFR-03). Chưa có hạ tầng PostgreSQL để dùng.

## Quyết định
1. **Lưu trữ:** `DocumentRepository` lưu trong bộ nhớ tiến trình, có khoá. Dữ liệu mất khi restart.
2. **Xử lý:** `DocumentService.upload` đọc và trích xuất PDF trong chính request. Trạng thái trả về là kết quả cuối (READY, NO_TEXT, ERROR), không có PROCESSING trung gian.
3. **Giới hạn đọc:** endpoint đọc tối đa 50 MB + 1 byte để chặn file quá lớn trước khi đưa vào bộ nhớ.

## Hệ quả
- Không đạt NFR-03 (5 phút) theo nghĩa bất đồng bộ; với PDF lớn, request có thể chậm. Cần đo trước khi nghiệm thu.
- Không đạt REL-03 (sao lưu) và TC-09/PD-04 (xoá hội thoại khi hết phiên). Hiện không có dữ liệu bền vững.
- US-202 "Đang xử lý" và "Thử lại" chưa có. Đây là phần của worker khi chuyển sang PostgreSQL.
- Repository là một lớp riêng để thay bằng adapter PostgreSQL mà không sửa service.

**Why:** muốn có bằng chứng end-to-end nhanh; hạ tầng chưa chốt (OQ-008) nên không nên khoá vào một CSDL.
**How to apply:** trước khi đưa vào sử dụng thật, thêm adapter PostgreSQL cho `DocumentRepository`, tách worker cho `process_document`, và đo lại NFR-03 với file 300 trang.
