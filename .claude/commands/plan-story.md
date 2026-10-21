---
description: Lập kế hoạch cho một user story trước khi code
argument-hint: <US-nnn>
---

Lập kế hoạch cho user story $ARGUMENTS:

1. Tìm story và AC trong `docs/02-requirements/PRD.md`; nếu AC mơ hồ hoặc mâu thuẫn với `docs/03-design/SAD.md`, dừng và hỏi.
2. Liệt kê từng AC, file trong `app/` và `tests/` cần đổi, và test sẽ chứng minh từng AC.
3. Nêu rõ phần nào nằm ngoài MVP (xem `docs/adr/0001-mvp-scope.md`).
4. Nếu có quyết định kiến trúc mới, đề xuất một ADR trong `docs/adr/`.
5. Không sửa code trong lệnh này.
