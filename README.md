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



```
DACN
├─ backend
│  ├─ .env
│  ├─ api
│  │  ├─ events.py
│  │  ├─ nlp.py
│  │  ├─ users.py
│  │  └─ __pycache__
│  │     ├─ events.cpython-311.pyc
│  │     ├─ events.cpython-314.pyc
│  │     ├─ nlp.cpython-311.pyc
│  │     ├─ nlp.cpython-314.pyc
│  │     ├─ users.cpython-311.pyc
│  │     └─ users.cpython-314.pyc
│  ├─ database.db
│  ├─ db.py
│  ├─ main.py
│  ├─ models
│  │  ├─ models.py
│  │  ├─ schemas.py
│  │  ├─ __init__.py
│  │  └─ __pycache__
│  │     ├─ models.cpython-311.pyc
│  │     ├─ models.cpython-314.pyc
│  │     ├─ schemas.cpython-311.pyc
│  │     ├─ schemas.cpython-314.pyc
│  │     ├─ __init__.cpython-311.pyc
│  │     └─ __init__.cpython-314.pyc
│  ├─ nlp
│  │  ├─ datetime_builder.py
│  │  ├─ location.py
│  │  ├─ name_extractor.py
│  │  ├─ preprocess.py
│  │  ├─ reminder.py
│  │  ├─ time_extractor.py
│  │  └─ __pycache__
│  │     ├─ datetime_builder.cpython-311.pyc
│  │     ├─ datetime_builder.cpython-314.pyc
│  │     ├─ location.cpython-311.pyc
│  │     ├─ location.cpython-314.pyc
│  │     ├─ name_extractor.cpython-311.pyc
│  │     ├─ name_extractor.cpython-314.pyc
│  │     ├─ preprocess.cpython-311.pyc
│  │     ├─ preprocess.cpython-314.pyc
│  │     ├─ reminder.cpython-311.pyc
│  │     ├─ reminder.cpython-314.pyc
│  │     ├─ time_extractor.cpython-311.pyc
│  │     └─ time_extractor.cpython-314.pyc
│  ├─ nlp_processor.py
│  ├─ package-lock.json
│  ├─ package.json
│  ├─ reminders.py
│  ├─ requirements.txt
│  ├─ scripts
│  │  ├─ debugmail.py
│  │  ├─ run_nlp_test.py
│  │  └─ __pycache__
│  │     └─ test_reminder.cpython-314.pyc
│  └─ __pycache__
│     ├─ db.cpython-311.pyc
│     ├─ db.cpython-314.pyc
│     ├─ main.cpython-311.pyc
│     ├─ main.cpython-314.pyc
│     ├─ models.cpython-311.pyc
│     ├─ nlp_processor.cpython-311.pyc
│     ├─ nlp_processor.cpython-314.pyc
│     ├─ reminders.cpython-314.pyc
│     ├─ reminders_clean.cpython-314.pyc
│     └─ __init__.cpython-311.pyc
├─ frontend
│  ├─ .env
│  ├─ eslint.config.js
│  ├─ index.html
│  ├─ package-lock.json
│  ├─ package.json
│  ├─ public
│  │  └─ vite.svg
│  ├─ requirement.txt
│  ├─ src
│  │  ├─ App.jsx
│  │  ├─ assets
│  │  │  └─ react.svg
│  │  ├─ components
│  │  │  ├─ Auth
│  │  │  │  ├─ Login.jsx
│  │  │  │  ├─ Register.jsx
│  │  │  │  └─ VerifyEmail.jsx
│  │  │  ├─ Common
│  │  │  │  ├─ ConfirmationModal.jsx
│  │  │  │  ├─ SearchBar.jsx
│  │  │  │  ├─ Toast.jsx
│  │  │  │  └─ ToastProvider.jsx
│  │  │  ├─ Events
│  │  │  │  ├─ Calendar.jsx
│  │  │  │  ├─ EventForm.jsx
│  │  │  │  ├─ EventItem.jsx
│  │  │  │  ├─ EventList.jsx
│  │  │  │  └─ NLPInput.jsx
│  │  │  └─ Layout
│  │  │     ├─ Header.jsx
│  │  │     └─ Layout.jsx
│  │  ├─ main.jsx
│  │  ├─ services
│  │  │  ├─ api.js
│  │  │  └─ auth.js
│  │  └─ styles
│  │     └─ App.css
│  └─ vite.config.js
└─ README.md

```
```
DACN
├─ backend
│  ├─ .env
│  ├─ api
│  │  ├─ events.py
│  │  ├─ nlp.py
│  │  ├─ users.py
│  │  └─ __pycache__
│  │     ├─ events.cpython-311.pyc
│  │     ├─ events.cpython-314.pyc
│  │     ├─ nlp.cpython-311.pyc
│  │     ├─ nlp.cpython-314.pyc
│  │     ├─ users.cpython-311.pyc
│  │     └─ users.cpython-314.pyc
│  ├─ database.db
│  ├─ db.py
│  ├─ main.py
│  ├─ models
│  │  ├─ models.py
│  │  ├─ schemas.py
│  │  ├─ __init__.py
│  │  └─ __pycache__
│  │     ├─ models.cpython-311.pyc
│  │     ├─ models.cpython-314.pyc
│  │     ├─ schemas.cpython-311.pyc
│  │     ├─ schemas.cpython-314.pyc
│  │     ├─ __init__.cpython-311.pyc
│  │     └─ __init__.cpython-314.pyc
│  ├─ nlp
│  │  ├─ datetime_builder.py
│  │  ├─ location.py
│  │  ├─ name_extractor.py
│  │  ├─ preprocess.py
│  │  ├─ reminder.py
│  │  ├─ time_extractor.py
│  │  └─ __pycache__
│  │     ├─ datetime_builder.cpython-311.pyc
│  │     ├─ datetime_builder.cpython-314.pyc
│  │     ├─ location.cpython-311.pyc
│  │     ├─ location.cpython-314.pyc
│  │     ├─ name_extractor.cpython-311.pyc
│  │     ├─ name_extractor.cpython-314.pyc
│  │     ├─ preprocess.cpython-311.pyc
│  │     ├─ preprocess.cpython-314.pyc
│  │     ├─ reminder.cpython-311.pyc
│  │     ├─ reminder.cpython-314.pyc
│  │     ├─ time_extractor.cpython-311.pyc
│  │     └─ time_extractor.cpython-314.pyc
│  ├─ nlp_processor.py
│  ├─ package-lock.json
│  ├─ package.json
│  ├─ reminders.py
│  ├─ requirements.txt
│  ├─ scripts
│  │  ├─ debugmail.py
│  │  ├─ run_nlp_test.py
│  │  └─ __pycache__
│  │     └─ test_reminder.cpython-314.pyc
│  └─ __pycache__
│     ├─ db.cpython-311.pyc
│     ├─ db.cpython-314.pyc
│     ├─ main.cpython-311.pyc
│     ├─ main.cpython-314.pyc
│     ├─ models.cpython-311.pyc
│     ├─ nlp_processor.cpython-311.pyc
│     ├─ nlp_processor.cpython-314.pyc
│     ├─ reminders.cpython-314.pyc
│     ├─ reminders_clean.cpython-314.pyc
│     └─ __init__.cpython-311.pyc
├─ frontend
│  ├─ .env
│  ├─ eslint.config.js
│  ├─ index.html
│  ├─ package-lock.json
│  ├─ package.json
│  ├─ public
│  │  └─ vite.svg
│  ├─ requirement.txt
│  ├─ src
│  │  ├─ App.jsx
│  │  ├─ assets
│  │  │  └─ react.svg
│  │  ├─ components
│  │  │  ├─ Auth
│  │  │  │  ├─ Login.jsx
│  │  │  │  ├─ Register.jsx
│  │  │  │  └─ VerifyEmail.jsx
│  │  │  ├─ Common
│  │  │  │  ├─ ConfirmationModal.jsx
│  │  │  │  ├─ SearchBar.jsx
│  │  │  │  ├─ Toast.jsx
│  │  │  │  └─ ToastProvider.jsx
│  │  │  ├─ Events
│  │  │  │  ├─ Calendar.jsx
│  │  │  │  ├─ EventForm.jsx
│  │  │  │  ├─ EventItem.jsx
│  │  │  │  ├─ EventList.jsx
│  │  │  │  └─ NLPInput.jsx
│  │  │  └─ Layout
│  │  │     ├─ Header.jsx
│  │  │     └─ Layout.jsx
│  │  ├─ main.jsx
│  │  ├─ services
│  │  │  ├─ api.js
│  │  │  └─ auth.js
│  │  └─ styles
│  │     └─ App.css
│  └─ vite.config.js
└─ README.md

```