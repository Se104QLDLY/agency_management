# 🏢 Agency Management Backend (Django REST Framework)

> Hệ thống backend cho phần mềm **quản lý đại lý**, hỗ trợ quản lý doanh số, công nợ, nhập xuất kho, quy định hệ thống, và thống kê dashboard.

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![Django](https://img.shields.io/badge/Django-4.2-green?logo=django)
![DRF](https://img.shields.io/badge/DRF-REST_API-red?logo=fastapi)
![Docker](https://img.shields.io/badge/Docker-ready-blue?logo=docker)
![CI](https://github.com/YOUR_USERNAME/YOUR_REPO/actions/workflows/django-ci.yml/badge.svg)

---

## 🚀 Tính năng nổi bật

✅ Xác thực bằng JWT + xác minh email

✅ CRUD đại lý, phân loại, địa phương

✅ Quản lý sản phẩm, nhập kho, xuất hàng

✅ Tạo phiếu thu, báo cáo công nợ và doanh số

✅ API dashboard tổng hợp

✅ Quản lý quy định hệ thống

✅ Swagger UI / Redoc / Docker / GitHub Actions

---

## 📦 Cấu trúc hệ thống
agency_management/

├── apps/

│   ├── accounts/      # User + Auth

│   ├── agencies/      # Đại lý, quận, loại

│   ├── inventory/     # Hàng hóa, nhập/xuất

│   ├── finance/       # Phiếu thu, báo cáo

│   ├── regulations/   # Cấu hình hệ thống

│   └── dashboard/     # API tổng hợp

├── config/            # Cấu hình Django

├── docker-compose.yml

├── Dockerfile

├── .env

└── .github/workflows/django-ci.yml


## ⚙️ Cài đặt cục bộ (Local)

```bash
# 1. Clone source
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO

# 2. Tạo và kích hoạt môi trường
python -m venv env
source env/bin/activate  # Windows: env\Scripts\activate

# 3. Cài đặt gói phụ thuộc
pip install -r requirements.txt

# 4. Cấu hình biến môi trường
cp .env.example .env  # Hoặc tự tạo .env với DB, Email config

# 5. Migrate & chạy server
python manage.py migrate
python manage.py runserver

## 🐳 Chạy bằng Docker

```bash
bash
Sao chépChỉnh sửa
docker-compose up --build

```

Truy cập app tại: [http://localhost:8000](http://localhost:8000/)

---

## 🔐 Xác thực bằng JWT

- Đăng nhập: `POST /api/token/`
- Làm mới token: `POST /api/token/refresh/`
- Đăng ký: `POST /api/accounts/register/`
- Xác minh email: `GET /api/accounts/verify-email/?token=...`

---

## 📘 Tài liệu API (Swagger)

- Swagger UI: [`/api/docs/`](http://localhost:8000/api/docs/)
- OpenAPI schema: [`/api/schema/`](http://localhost:8000/api/schema/)
- Redoc: [`/api/redoc/`](http://localhost:8000/api/redoc/)

---

## 🛠️ CI/CD – GitHub Actions

Định nghĩa tại: `.github/workflows/django-ci.yml`

- Tự động test khi push/pull
- Chạy migrate + test DB PostgreSQL

---

## 📬 Gửi email xác minh

- Cấu hình email qua `.env`:
    
    ```
    env
    Sao chépChỉnh sửa
    EMAIL_HOST_USER=your_email@gmail.com
    EMAIL_HOST_PASSWORD=your_app_password
    
    ```
    

---

## 🤝 Đóng góp & phát triển

Pull requests luôn được hoan nghênh!

Vui lòng tạo branch riêng và mô tả rõ ràng 🙌

---

## 📄 Giấy phép

MIT License © 2025 – Agency Management Team
