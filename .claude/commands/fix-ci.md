---
description: Sửa một job CI đang đỏ, lặp cho đến khi mọi cổng L0 xanh
argument-hint: <tên job hoặc log>
---

Sửa lỗi CI: $ARGUMENTS

1. Đọc log của job lỗi và tìm dòng lỗi đầu tiên; đừng sửa theo triệu chứng cuối.
2. Tái hiện cục bộ bằng đúng lệnh trong `.github/workflows/ci.yml` (xem `AGENTS.md`).
3. Sửa nguyên nhân trong `app/`, `tests/`, `scripts/` hoặc cấu hình. Không xoá test, không thêm `skip`, không hạ ngưỡng coverage.
4. Commit với mã US-nnn liên quan, ví dụ `fix(ci): ... Refs: US-301`.
5. Lặp lại cho đến khi lệnh cục bộ pass; báo lại các cổng còn đỏ nếu có.
