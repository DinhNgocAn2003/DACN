# ĐỒ ÁN CHUYÊN NGÀNH  - Trợ lý quản lý lịch trình cá nhân
Một dự án quản lý sự kiện với NLP (xử lý ngôn ngữ tự nhiên) để tạo/quản lý sự kiện.
# Thông tin sinh viên
- Sinh viên:  ĐINH NGỌC ÂN
- MSSV:       3121410062

# Mô tả dự án
- Backend: API và bộ xử lý NLP để trích xuất thông tin sự kiện (thời gian, địa điểm, tên, ...).
- Frontend: Giao diện React (Vite) cho phép người dùng tạo và xem sự kiện.

## Cấu trúc chính
- `backend/` – mã Python cho API, xử lý NLP và models.
  - `main.py` – điểm vào (server/API).
  - `nlp_processor.py` và `nlp/` – logic xử lý ngôn ngữ.
  - `api/` – route xử lý HTTP.
  - `models/` – định nghĩa mô hình và schema.
  - `tests/` – test cho phần NLP.

- `frontend/` – ứng dụng web (Vite + React).
- `requirements.txt` – phụ thuộc Python chung (gốc).
- `backend/requirements.txt` – phụ thuộc riêng cho backend.

# Yêu cầu
- Python (xem tại https://www.python.org/downloads/)
- Node.js và npm (xem tại https://nodejs.org/en/download)


# Cài đặt ở backend
1. Đến thư mục backend (từ thư mục gốc)
```powershell
cd .\backend\
```
2. Cài node modules và chạy dev server - Với các modules cần thiết đã được liệt kê trong requirement.txt
```powershell
python -m pip install -r requirements.txt 
```


# Cài đặt ở frontend
1. Đến thư mục backend (từ thư mục gốc)
```powershell
cd frontend
```
2. Cài đặt npm
```powershell
npm install
```
2. Mở trình duyệt theo địa chỉ mà Vite hiển thị (mặc định thường là `http://localhost:5173`).

# Run code
1. Đến thư mục backend (từ thư mục gốc)
```powershell
cd .\backend\
```
2. Chạy dòng lệnh
```powershell
npm run dev:all
```

## Ghi chú phát triển
- Thay đổi NLP nằm trong `backend/nlp/` — các module tách biệt cho thời gian, địa điểm, tên.
- API routes có trong `backend/api/`.


