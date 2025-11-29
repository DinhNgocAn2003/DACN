# Hướng dẫn cài đặt Backend (DACN)

Tài liệu ngắn này hướng dẫn cách chuẩn bị môi trường Python và cài các phụ thuộc để chạy backend.

Yêu cầu:
- Python 3.10+ (khuyến nghị 3.11)
- pip

1) Chuẩn bị virtualenv (Windows PowerShell)

```powershell
cd d:\code\DACN\backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2) Cài dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

(Lưu ý: file `requirements.txt` nằm ở `backend/requirements.txt`. Nếu bạn cài từ root, dùng đường dẫn tương ứng.)

3) Biến môi trường quan trọng (ví dụ trên PowerShell)

- Cấu hình DB: (mặc định repo dùng SQLite nên không cần thêm biến này cho dev.)
- SMTP (nếu muốn gửi email thật):

```powershell
$env:SMTP_HOST='smtp.gmail.com'
$env:SMTP_PORT='465'      # repo hiện cấu hình dùng implicit SSL 465
$env:SMTP_USER='your.email@gmail.com'
$env:SMTP_PASS='your_app_password_here'  # với Gmail: App Password nếu bật 2FA
$env:FROM_EMAIL='your.email@gmail.com'
```

- Tùy chọn debug SMTP:

```powershell
$env:SMTP_DEBUG='1'
```

4) Chạy server backend (development)

```powershell
# trong folder backend, với venv active
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

5) Chạy scheduler (reminders)

Có 2 cách:
- Chạy in-process: gọi `start_scheduler()` trong `backend/main.py` ở event startup (nếu bạn muốn scheduler chạy cùng với Uvicorn/ FastAPI).
- Chạy độc lập: chạy `reminders.py` như tiến trình riêng (dùng PowerShell Start-Process / task scheduler / nssm) — repo có `start_scheduler()` để scheduler chạy.

Test nhanh reminder (không cần scheduler liên tục):

```powershell
# Thiết lập env SMTP nếu muốn gửi thật (xem trên)
python .\scripts\trigger_reminder_immediate.py
```

Script trên sẽ tìm/tao event test, đặt start_time = now và `time_reminder = 0`, gọi job runner và in kết quả. Nếu SMTP chưa cấu hình, hệ thống sẽ in nội dung email ra console và vẫn cập nhật `reminder_sent_at` trong DB.

6) Notes/khuyến nghị
- Với Gmail, bắt buộc bật 2FA và tạo App Password để dùng cho `SMTP_PASS` (Google chặn mật khẩu thông thường). Hoặc dùng dịch vụ SMTP chuyên dụng (SendGrid, Mailgun, Amazon SES).
- Hiện code lưu naive datetimes (local). Với môi trường production, khuyến nghị chuẩn hóa timezone-aware UTC.
- Đừng commit secrets (SMTP_PASS, DB password) vào git. Dùng secret manager hoặc biến môi trường trên server.

Nếu bạn muốn, tôi có thể:
- Thêm dòng `start_scheduler()` vào `backend/main.py` trong sự kiện startup (tự động bật scheduler khi chạy app).
- Hoặc cho hướng dẫn chi tiết để chạy `reminders.py` như service trên Windows (Task Scheduler / nssm) hoặc Linux (systemd).
