# 🏢 Đại lý Quản Lý Hệ Thống - SE104 QLDLY

Hệ thống quản lý đại lý phân phối được xây dựng bằng **Django REST Framework**. Phục vụ cho nhu cầu quản lý hoạt động của các đại lý, nhà phân phối và quản trị viên, bao gồm: quản lý thông tin đại lý, lập phiếu xuất/nhập hàng, thanh toán, báo cáo thống kê...

## 🔧 Công nghệ sử dụng

- 🐍 Python 3.10+
- 🌐 Django 4.x
- 🔌 Django REST Framework
- 🔐 JWT Authentication (SimpleJWT)
- 🧾 Swagger API docs (`drf-yasg`)
- 🧮 PostgreSQL / SQLite
- 📄 ReportLab / openpyxl / pandas (báo cáo PDF/Excel)
- 📬 SMTP (xác thực email)

---

## 📦 Cấu trúc thư mục chính
agency_management/

├── apps/

│ ├── accounts/ # Quản lý người dùng và vai trò

│ ├── agencies/ # Quản lý đại lý, loại đại lý, quận

│ ├── inventory/ # Quản lý phiếu xuất, tồn kho

│ ├── finance/ # Quản lý công nợ và thanh toán

│ ├── dashboard/ # API tổng quan (thống kê nhanh)

│ └── regulation/ # Ràng buộc, quy định kiểm tra dữ liệu

│
├── config/ # Cấu hình dự án (settings, urls)

├── media/ # Upload tệp báo cáo PDF, Excel

└── manage.py # Entrypoint chạy project


---

## 🔐 Chức năng chính

### 📁 1. Quản lý người dùng
- Phân quyền theo vai trò: Quản trị viên, Nhà phân phối, Đại lý
- Gửi email xác thực, ghi lịch sử đăng nhập

### 🏪 2. Quản lý đại lý
- Thêm, sửa, xóa, tìm kiếm đại lý
- Kiểm tra số lượng đại lý tối đa trong quận
- Kiểm tra nợ đại lý không vượt quá giới hạn

### 📦 3. Quản lý phiếu xuất / nhập hàng
- Lập, sửa, xóa phiếu nhập/xuất
- Kiểm tra tồn kho, công nợ, quy định
- Tự động cập nhật số lượng tồn kho và nợ sau mỗi thao tác

### 📊 4. Dashboard thống kê
- Doanh thu theo tháng
- Top đại lý nợ cao nhất
- Tồn kho sản phẩm

### 📤 5. Xuất báo cáo
- Xuất báo cáo doanh số, tồn kho theo quận / loại đại lý
- Hỗ trợ định dạng PDF & Excel

---

## ▶️ Cài đặt và chạy local

```bash
git clone https://github.com/Se104QLDLY/agency_management.git
cd agency_management

python -m venv env
source env/bin/activate  # (hoặc env\Scripts\activate trên Windows)

pip install -r requirements.txt

# Cấu hình .env file (tạo file .env)
cp .env.example .env

# Di chuyển database ban đầu (SQLite/PostgreSQL)
python manage.py migrate

# Tạo tài khoản quản trị
python manage.py createsuperuser

# Chạy server
python manage.py runserver
```

🧪 API Documentation
Truy cập tại http://localhost:8000/swagger/ để xem tài liệu Swagger UI.

👥 Nhóm phát triển: Nhóm 11
Nhóm SE104 UIT HCM

📜 Giấy phép
This project is licensed under the MIT License - see the LICENSE.md file for details.


---

✅ **Tips**:
- Có thể chia phần `Chức năng` tương ứng với các **use case** bạn đã trình bày trong chương 3 để khớp giữa báo cáo và source code.
- Bạn có thể thêm badge tự động test hoặc deploy nếu nhóm bạn dùng CI/CD trên GitHub Actions.


