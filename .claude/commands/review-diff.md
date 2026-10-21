---
description: Review L1 (advisory) theo rubric 7 tiêu chí, 0–2 điểm mỗi tiêu chí
---

Review diff hiện tại (`git diff origin/main...HEAD` hoặc thay đổi chưa commit) theo rubric:

| Tiêu chí | Câu hỏi |
|---|---|
| Đúng AC | Diff có đáp ứng AC của US được tag trong commit không? |
| Test | Có test chứng minh AC, gồm biên và lỗi không? |
| Thiết kế | Trách nhiệm có tách module, phụ thuộc có đi qua port không? |
| An toàn | Có lộ secret, có injection (`innerHTML`, SQL), có kiểm tra đầu vào không? |
| Hiệu năng | Có vòng lặp hoặc thao tác O(n²) không cần thiết trên đường nóng không? |
| Dễ đọc | Tên rõ, hàm ngắn, comment giải thích "vì sao"? |
| Truy vết | Commit có mã US-nnn không? |

Quy tắc:
- Mỗi nhận xét phải trích dẫn file và dòng bị lỗi.
- Chấm mỗi tiêu chí 0, 1 hoặc 2. Điểm 0 ở bất kỳ tiêu chí nào là blocker.
- Chỉ đề xuất sửa, không tự approve và không merge.
