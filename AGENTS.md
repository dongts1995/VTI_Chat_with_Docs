# AGENTS.md — hướng dẫn cho agent làm việc trên repo này

## Nguồn sự thật
- Đặc tả nằm trong `docs/` (BRD, PRD, SAD, Blueprint, use case). Đây là **nguồn sự thật duy nhất**.
- AC chưa rõ hoặc mâu thuẫn giữa các tài liệu: **dừng lại và hỏi**, không tự đoán.
- Chọn công nghệ mới hoặc đổi quyết định kiến trúc: viết ADR trong `docs/adr/` trước khi code.

## Stack
- Python **3.11+** (ADR-0001), FastAPI, pypdf. Dev: pytest, pytest-cov, httpx, ruff, mypy (strict), pip-audit.
- Giao diện: HTML/CSS/JS thuần trong `app/static/`, không build step.

## Lệnh
```bash
pip install -e ".[dev]"          # cài đặt
uvicorn app.main:app --reload    # chạy, mở http://127.0.0.1:8000
pytest                           # test + coverage (cổng 70%)
ruff check app tests && ruff format app tests
mypy                             # type check (files = app)
python scripts/check_traceability.py origin/main..HEAD   # mỗi commit có US-nnn
```

## Quy ước code
- Ngôn ngữ: tên biến/hàm tiếng Anh; thông báo gửi người dùng và comment nghiệp vụ tiếng Việt.
- Mỗi hàm nghiệp vụ có mã US/AC trong comment hoặc test name khi liên quan.
- Lỗi người dùng thấy đi qua `AppError` (problem+json), không để lộ traceback.
- Nội dung tài liệu và câu trả lời là **dữ liệu không tin cậy**: không dùng `innerHTML`, không log nội dung.
- Không thêm dependency mới khi chưa ghi lý do trong commit.

## Commit
- Conventional Commits: `feat(...)`, `fix(...)`, `test(...)`, `docs(...)`, `chore(...)`, `ci(...)`.
- Mỗi commit có ít nhất một mã `US-nnn` trong thông điệp (cổng traceability trong CI).
- Commit nhỏ, một thay đổi logic mỗi commit.

## Quyền hạn của agent
- **Được sửa:** `app/`, `tests/`, `scripts/`, `.github/`, `README.md`, `AGENTS.md`, `docs/adr/`, `docs/traceability.md`.
- **Không được sửa:** `docs/02-requirements/`, `docs/03-design/`, `docs/04-design/`, `docs/requirements/`, `docx/` (baseline đặc tả; thay đổi cần người phê duyệt).
- Không tự approve PR. Agent review (L1) chỉ đề xuất, không merge.

## Điều cấm
- Không commit secret, token, file `.env`, dữ liệu PDF thật của khách hàng.
- Không xoá hoặc `skip` test để CI xanh. Sửa code, không sửa test cho pass.
- Không mock toàn bộ phần lõi khi viết test tích hợp (`tests/test_qa_api.py` và `tests/test_upload_api.py` dùng PDF thật).
- Không đưa tài liệu người dùng vào log hoặc dữ liệu phân tích.

## Vòng lặp làm việc
plan (`/plan-story`) → code → test (`/gen-tests`) → review (`/review-diff`) → sửa lỗi CI (`/fix-ci`); dừng khi mọi cổng L0 xanh.
