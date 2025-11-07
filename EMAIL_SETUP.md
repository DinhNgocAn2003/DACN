# 📧 Hướng Dẫn Cấu Hình Email Reminder

## 🔧 Cấu hình Gmail để gửi email

### Bước 1: Tạo App Password cho Gmail

1. Đăng nhập vào Gmail của bạn
2. Truy cập: https://myaccount.google.com/security
3. Bật **2-Step Verification** (Xác thực 2 bước)
4. Sau khi bật, tìm **App passwords** (Mật khẩu ứng dụng)
5. Chọn **Mail** và **Windows Computer**
6. Click **Generate** → Copy mật khẩu 16 ký tự

### Bước 2: Cập nhật file `email_reminder.py`

Mở file `email_reminder.py` và thay đổi:

```python
# Dòng 8-10
SENDER_EMAIL = "your-email@gmail.com"      # Thay bằng email của bạn
SENDER_PASSWORD = "your-app-password"       # Thay bằng App Password vừa tạo
```

Ví dụ:
```python
SENDER_EMAIL = "nguyenvana@gmail.com"
SENDER_PASSWORD = "abcd efgh ijkl mnop"  # 16 ký tự từ Gmail
```

---

## 🚀 Cách sử dụng

### 1. Gửi email thủ công từ ứng dụng
- Đăng nhập vào ứng dụng
- Click nút **"📧 Gửi email tổng hợp"**
- Kiểm tra hộp thư đến

### 2. Gửi email tự động theo lịch

#### Cách 1: Chạy script định kỳ
```bash
# Chạy script kiểm tra và gửi email
python email_reminder.py
```

#### Cách 2: Tự động hóa với Task Scheduler (Windows)

1. Mở **Task Scheduler**
2. Create Basic Task
3. Tên: "Calendar Email Reminder"
4. Trigger: Daily hoặc theo giờ
5. Action: Start a program
   - Program: `C:\Users\...\python.exe`
   - Arguments: `D:\code\doAn\email_reminder.py`
6. Finish

#### Cách 3: Tự động hóa với Cron (Linux/Mac)

```bash
# Mở crontab
crontab -e

# Thêm dòng này để chạy mỗi 15 phút
*/15 * * * * /usr/bin/python3 /path/to/email_reminder.py

# Hoặc chạy mỗi sáng 8h
0 8 * * * /usr/bin/python3 /path/to/email_reminder.py
```

---

## 📋 Các loại email được gửi

### 1. Email Nhắc Nhở Sự Kiện
- Gửi trước sự kiện X phút (theo cài đặt `time_reminder`)
- Nội dung: Tên sự kiện, thời gian, địa điểm

### 2. Email Tổng Hợp Hàng Ngày
- Liệt kê tất cả sự kiện trong 24h tới
- Có thể gửi thủ công hoặc tự động mỗi sáng

---

## 🔍 Kiểm tra & Debug

### Test gửi email:
```python
# Thêm vào cuối email_reminder.py
if __name__ == "__main__":
    # Test với user_id = 1
    send_daily_summary_email(1)
```

### Lỗi thường gặp:

**❌ SMTPAuthenticationError**
- Kiểm tra lại email và App Password
- Đảm bảo đã bật 2-Step Verification

**❌ SMTPException**
- Kiểm tra kết nối internet
- Đảm bảo cổng 587 không bị chặn

**❌ No email sent**
- Kiểm tra user có email trong database không
- Kiểm tra có sự kiện trong 24h tới không

---

## 📝 Lưu ý

- ✅ Mỗi email được gửi 1 lần duy nhất cho mỗi sự kiện
- ✅ Email tổng hợp có thể gửi nhiều lần
- ✅ Không gửi email cho sự kiện đã qua
- ✅ Hỗ trợ HTML, responsive trên mobile

---

## 🎯 Tùy chỉnh nâng cao

### Thay đổi thời gian kiểm tra email:
```python
# email_reminder.py, dòng 176
if -5 <= time_diff <= 5:  # Thay 5 thành số phút khác
```

### Thay đổi template email:
- Chỉnh sửa phần `html_content` trong hàm `send_event_reminder_email()`
- Có thể thêm logo, màu sắc, style tùy thích

### Sử dụng email server khác (không phải Gmail):
```python
SMTP_SERVER = "smtp.office365.com"  # Outlook
SMTP_PORT = 587

# Hoặc
SMTP_SERVER = "smtp.mail.yahoo.com"  # Yahoo
SMTP_PORT = 465
```

---

Chúc bạn sử dụng hiệu quả! 🎉
