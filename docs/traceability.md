# Ma trận truy vết: US ↔ AC ↔ code ↔ test

> Cập nhật: 2026-10-21. Trạng thái: **Covered** = có test tự động pass · **Partial** = có một phần, phần còn lại ghi rõ · **Not done** = chưa làm, ghi lý do · **Manual** = cần người đánh giá.
>
> Tài liệu nguồn không có mã FR riêng; truy vết dùng mã US của PRD §3. Mỗi commit phải có mã US (cổng CI `scripts/check_traceability.py`).

## Hai user story xương sống (DoD: 100% AC có test tự động)

### US-201 — Tải PDF lên kho
| AC | Nội dung rút gọn | Trạng thái | Code | Test / ghi chú |
|---|---|---|---|---|
| AC1 | Tải PDF ≤ 50 MB, file hiện trong danh sách | Partial | `app/services.py` `DocumentService.upload`, `app/main.py` | `test_pdf_upload_is_accepted_and_ready`, `test_uploaded_document_appears_in_list`. Thiếu trạng thái "Đang tải lên" và % tiến độ (chỉ có sau khi request xong). |
| AC2 | Chọn 10 file, mỗi file có trạng thái riêng | Partial | `app/static/app.js` `uploadFiles` | Giao diện gửi tuần tự, mỗi file một kết quả. Chưa có test tự động cho UI; chưa thử 10 file. |
| AC3 | File sai định dạng / > 50 MB bị từ chối có lý do, file khác vẫn tải | Covered (backend) | `app/services.py` | `test_non_pdf_extension_is_rejected`, `test_pdf_extension_without_pdf_signature_is_rejected`, `test_file_over_50_mb_is_rejected_with_reason`. "File khác vẫn tải" đúng nhờ vòng lặp UI, chưa có test. |

### US-202 — Trạng thái xử lý
| AC | Nội dung rút gọn | Trạng thái | Code | Test / ghi chú |
|---|---|---|---|---|
| AC1 | 300 trang, 50 MB, sẵn sàng ≤ 5 phút | Not done | — | Không đo. Xử lý đồng bộ (ADR-0003); chưa có benchmark NFR-03. |
| AC2 | Câu hỏi khi file đang xử lý có ghi chú "1 tài liệu đang được xử lý" | Not done | — | MVP không có trạng thái PROCESSING (ADR-0003). |
| AC3 | Lỗi có lý do thường ngày và nút "Thử lại" | Partial | `app/pdf_text.py` | Lý do: `test_corrupt_pdf_is_flagged_error_with_reason`, `test_password_protected_pdf_is_flagged_error`. Nút "Thử lại" chưa có. |

### US-205 — Nhận diện PDF scan (P1, làm kèm)
| Mục | Trạng thái | Code | Test / ghi chú |
|---|---|---|---|
| 10/10 file scan có "Không đọc được chữ", không được trích | Covered (một trường hợp) | `app/pdf_text.py` `has_extractable_text` | `test_scanned_pdf_is_flagged_no_text`, `test_scanned_document_is_never_used_as_a_source`. Chưa có bộ 10 file thật. |

### US-301 — Hỏi bằng ngôn ngữ tự nhiên
| AC | Nội dung rút gọn | Trạng thái | Code | Test / ghi chú |
|---|---|---|---|---|
| AC1 | Câu hỏi tiếng Việt nhận câu trả lời tiếng Việt | Partial | `app/retrieval.py`, `app/answering.py` | `test_question_is_answered_from_ready_document`. Câu trả lời là câu trích từ tài liệu nên giữ ngôn ngữ của tài liệu; không dịch. |
| AC2 | Câu hỏi tiếng Anh nhận câu trả lời tiếng Anh | Partial | như trên | `test_english_question_uses_same_index`. Chỉ khớp khi tài liệu cùng ngôn ngữ (ADR-0002). |
| AC3 | Ô trống không gửi được | Covered (API) | `app/services.py` `QuestionService.ask` | `test_blank_question_is_rejected`. Vô hiệu hoá nút Gửi ở UI chưa có test tự động. |
| AC4 | > 2.000 ký tự: cảnh báo màu, nút Gửi bị vô hiệu | Partial | `app/services.py`, `app/static/index.html` | API trả 422: `test_question_over_2000_characters_is_rejected`. UI dùng `maxlength` nên cắt bớt, không cảnh báo màu. |

### US-302 — Tổng hợp từ nhiều tài liệu
| AC | Nội dung rút gọn | Trạng thái | Code | Test / ghi chú |
|---|---|---|---|---|
| AC1 | Thông tin ở 2 tài liệu → trích cả 2 | Covered | `app/retrieval.py` `PassageIndex.search` | `test_answer_combines_information_from_two_documents` |
| AC2 | Bộ 15 câu hỏi ≥ 80% đúng và đủ | Manual / Not done | — | Chưa có bộ câu hỏi và chưa chấm. Thuộc US-402 (P2, ngoài MVP). |
| AC3 | Tài liệu đã gỡ không được trích | Not done | — | US-204 hoãn (ADR-0001). |

### US-303 — Trích dẫn tài liệu và trang
| AC | Nội dung rút gọn | Trạng thái | Code | Test / ghi chú |
|---|---|---|---|---|
| AC1 | Mỗi đoạn có [n]; cuối có danh sách "Tên — trang X" | Covered | `app/answering.py`, `app/services.py`, `app/static/app.js` | `test_every_passage_has_a_numbered_citation_with_file_and_page`, `test_page_number_points_to_the_page_containing_the_answer` |
| AC2 | 30 trích dẫn ngẫu nhiên, ≥ 90% đúng trang | Manual / Not done | — | Cần người mở PDF để chấm. |
| AC3 | Không có trích dẫn → "không tìm thấy" | Covered | `app/services.py` | `test_question_without_match_returns_not_found_with_document_count` |

### US-304 — Báo "không tìm thấy"
| AC | Nội dung rút gọn | Trạng thái | Code | Test / ghi chú |
|---|---|---|---|---|
| AC1 | Thông báo "Không tìm thấy … trong N tài liệu" kèm gợi ý | Covered | `app/services.py` | `test_question_without_match_returns_not_found_with_document_count` |
| AC2 | Bộ 10 câu không có đáp án, ≥ 9 "không tìm thấy" | Manual / Not done | — | Chưa có bộ câu hỏi. |
| AC3 | Giao diện trung tính, không dùng thông tin ngoài | Partial | `app/static/style.css` (`.not-found`) | Có kiểu trung tính; không có test UI. Thông tin ngoài: không có vì không gọi LLM (ADR-0002). |

## Ngoài MVP (ghi nhận, chưa làm)
| Story | Lý do | Ghi chú |
|---|---|---|
| US-101 → US-103 (đăng nhập, phân quyền, hết phiên) | Chưa chốt IdP (SAD TC-07, IF-01) | Là rủi ro bảo mật lớn; **không được đưa ra production khi chưa có**. |
| US-203 (danh sách + lọc), US-204 (gỡ tài liệu), US-206 (trùng lặp) | P1/P2, không thuộc hai story xương sống | Danh sách cơ bản đã có qua `GET /api/v1/documents`. |
| US-305 (mở trang nguồn) | P1 | Trích dẫn hiện có tên file và trang, chưa có trình xem PDF. |
| US-306, US-310 (streaming, dừng) | P1 | Trả lời một lần. |
| US-307, US-308, US-309, US-311 | P1/P2 | Chưa làm. |
| US-401, US-402 (số liệu, bộ kiểm thử) | P1/P2 | Chưa làm. |

## Definition of Done (PRD/slide Day 5)
| Mục | Trạng thái |
|---|---|
| Chạy bằng 1 lệnh; README 5 dòng: cài, cấu hình, chạy, test | Covered — [README.md](../README.md) |
| 100% AC của 2 user story có test tự động | **Not met.** Một số AC chỉ Partial hoặc Manual; xem các bảng trên. |
| Coverage ≥ 70% | Covered — 99% local (`pytest`); cổng CI `--cov-fail-under=70`. |
| CI xanh: lint, type, test, build, secret scan | Pending — workflow có trong `.github/workflows/ci.yml`; chưa chạy trên GitHub tại thời điểm viết. |
| 1 approver không phải người viết, checklist đã tick | Pending — chưa có PR được review. |
| Ma trận truy vết US ↔ FR ↔ code ↔ test | Partial — FR không có trong tài liệu nguồn; dùng US. |
