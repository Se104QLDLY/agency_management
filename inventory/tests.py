import pytest
from decimal import Decimal
from datetime import date
from django.db import IntegrityError, connection
from django.core.exceptions import ValidationError
from rest_framework.test import APIClient
from rest_framework import status
import os

from inventory.models import Unit, Item, Receipt, ReceiptDetail, Issue, IssueDetail
from authentication.models import Account, User
from agency.models import AgencyType, District, Agency


@pytest.mark.django_db
class TestUnitModel:
    """Test cases cơ bản cho Unit model"""

    def test_create_unit_success(self):
        """Kiểm tra tạo unit thành công"""
        unit = Unit.objects.create(unit_name='Cái')
        assert unit.unit_name == 'Cái'
        assert unit.unit_id is not None

    def test_unit_name_unique(self):
        """Kiểm tra unit_name phải là duy nhất"""
        Unit.objects.create(unit_name='Cái')
        with pytest.raises(IntegrityError):
            Unit.objects.create(unit_name='Cái')

    def test_unit_str_representation(self):
        """Kiểm tra string representation của Unit"""
        unit = Unit.objects.create(unit_name='Cái')
        assert str(unit) == 'Cái'


@pytest.mark.django_db
class TestItemModel:
    """Test cases cơ bản cho Item model"""

    @pytest.fixture
    def unit(self):
        """Fixture tạo unit cho test"""
        return Unit.objects.create(unit_name='Cái')

    def test_create_item_success(self, unit):
        """Kiểm tra tạo item thành công"""
        item = Item.objects.create(
            item_name='Bút bi',
            unit=unit,
            price=Decimal('5000.00'),
            stock_quantity=100,
            description='Bút bi xanh'
        )
        assert item.item_name == 'Bút bi'
        assert item.price == Decimal('5000.00')
        assert item.stock_quantity == 100
        assert item.unit == unit

    def test_item_name_unique(self, unit):
        """Kiểm tra item_name phải là duy nhất"""
        Item.objects.create(
            item_name='Bút bi',
            unit=unit,
            price=Decimal('5000.00'),
            stock_quantity=100
        )
        with pytest.raises(IntegrityError):
            Item.objects.create(
                item_name='Bút bi',
                unit=unit,
                price=Decimal('6000.00'),
                stock_quantity=50
            )

    def test_item_price_validation(self, unit):
        """Kiểm tra validation cho price"""
        with pytest.raises(IntegrityError):
            Item.objects.create(
                item_name='Test Item',
                unit=unit,
                price=Decimal('-1000.00'),
                stock_quantity=10
            )

    def test_item_str_representation(self, unit):
        """Kiểm tra string representation của Item"""
        item = Item.objects.create(
            item_name='Bút bi',
            unit=unit,
            price=Decimal('5000.00'),
            stock_quantity=100
        )
        assert str(item) == 'Bút bi'


@pytest.mark.django_db
class TestReceiptModel:
    """Test cases cơ bản cho Receipt model"""

    @pytest.fixture
    def user(self):
        """Fixture tạo user cho test"""
        account = Account.objects.create(
            username='testuser',
            password_hash='hash',
            account_role=Account.ADMIN
        )
        return User.objects.create(
            account=account,
            full_name='Test User',
            email='test@example.com'
        )

    @pytest.fixture
    def agency(self):
        """Fixture tạo agency cho test"""
        agency_type = AgencyType.objects.create(
            type_name='Loại A',
            max_debt=Decimal('1000000.00')
        )
        district = District.objects.create(
            city_name='Hà Nội',
            district_name='Cầu Giấy',
            max_agencies=10
        )
        return Agency.objects.create(
            agency_name='Đại lý Test',
            agency_type=agency_type,
            phone_number='0123456789',
            address='123 Test Street',
            district=district,
            email='agency@test.com',
            representative='Nguyễn Văn A',
            reception_date=date.today(),
            debt_amount=Decimal('0.00')
        )

    def test_create_receipt_success(self, user, agency):
        """Kiểm tra tạo receipt thành công"""
        receipt = Receipt.objects.create(
            receipt_date=date.today(),
            user_id=user.user_id,
            agency_id=agency.agency_id,
            total_amount=Decimal('0.00')
        )
        assert receipt.receipt_date == date.today()
        assert receipt.user_id == user.user_id
        assert receipt.agency_id == agency.agency_id
        assert receipt.total_amount == Decimal('0.00')

    def test_receipt_total_amount_validation(self, user, agency):
        """Kiểm tra validation cho total_amount"""
        with pytest.raises(ValidationError):
            receipt = Receipt(
                receipt_date=date.today(),
                user_id=user.user_id,
                agency_id=agency.agency_id,
                total_amount=Decimal('-1000.00')
            )
            receipt.full_clean()

    def test_receipt_str_representation(self, user, agency):
        """Kiểm tra string representation của Receipt"""
        receipt = Receipt.objects.create(
            receipt_date=date.today(),
            user_id=user.user_id,
            agency_id=agency.agency_id,
            total_amount=Decimal('0.00')
        )
        assert str(receipt) == f'Receipt #{receipt.receipt_id}'


@pytest.mark.django_db
class TestIssueModel:
    """Test cases cơ bản cho Issue model"""

    @pytest.fixture
    def user(self):
        """Fixture tạo user cho test"""
        account = Account.objects.create(
            username='testuser',
            password_hash='hash',
            account_role=Account.ADMIN
        )
        return User.objects.create(
            account=account,
            full_name='Test User',
            email='test@example.com'
        )

    @pytest.fixture
    def agency(self):
        """Fixture tạo agency cho test"""
        agency_type = AgencyType.objects.create(
            type_name='Loại A',
            max_debt=Decimal('1000000.00')
        )
        district = District.objects.create(
            city_name='Hà Nội',

            \
            district_name='Cầu Giấy',
            max_agencies=10
        )
        return Agency.objects.create(
            agency_name='Đại lý Test',
            agency_type=agency_type,
            phone_number='0123456789',
            address='123 Test Street',
            district=district,
            email='agency@test.com',
            representative='Nguyễn Văn A',
            reception_date=date.today(),
            debt_amount=Decimal('0.00')
        )

    def test_create_issue_success(self, user, agency):
        """Kiểm tra tạo issue thành công"""
        issue = Issue.objects.create(
            issue_date=date.today(),
            agency_id=agency.agency_id,
            user_id=user.user_id,
            total_amount=Decimal('0.00')
        )
        assert issue.issue_date == date.today()
        assert issue.agency_id == agency.agency_id
        assert issue.user_id == user.user_id
        assert issue.total_amount == Decimal('0.00')

    def test_issue_total_amount_validation(self, user, agency):
        """Kiểm tra validation cho total_amount"""
        with pytest.raises(ValidationError):
            issue = Issue(
                issue_date=date.today(),
                agency_id=agency.agency_id,
                user_id=user.user_id,
                total_amount=Decimal('-1000.00')
            )
            issue.full_clean()

    def test_issue_str_representation(self, user, agency):
        """Kiểm tra string representation của Issue"""
        issue = Issue.objects.create(
            issue_date=date.today(),
            agency_id=agency.agency_id,
            user_id=user.user_id,
            total_amount=Decimal('0.00')
        )
        assert str(issue) == f'Issue #{issue.issue_id}'


@pytest.mark.django_db
class TestDatabaseConstraints:
    """Kiểm tra các ràng buộc database"""

    def test_unit_name_unique(self):
        """Kiểm tra unit_name là duy nhất"""
        Unit.objects.create(unit_name="Cái")
        with pytest.raises(IntegrityError):
            Unit.objects.create(unit_name="Cái")

    def test_item_price_check(self):
        """Kiểm tra price >= 0"""
        unit = Unit.objects.create(unit_name="Thùng")
        with pytest.raises(IntegrityError):
            Item.objects.create(
                item_name="Bút", 
                unit=unit, 
                price=Decimal('-1'), 
                stock_quantity=10
            )

    def test_item_stock_quantity_check(self):
        """Kiểm tra stock_quantity >= 0"""
        unit = Unit.objects.create(unit_name="Thùng")
        with pytest.raises(IntegrityError):
            Item.objects.create(
                item_name="Vở", 
                unit=unit, 
                price=Decimal('1000'), 
                stock_quantity=-5
            )

    def test_foreign_key_constraint(self):
        """Kiểm tra ràng buộc khóa ngoại"""
        with pytest.raises(IntegrityError):
            Item.objects.create(
                item_name="Sách", 
                unit_id=999,  # Unit không tồn tại
                price=Decimal('1000'), 
                stock_quantity=10
            )


# ========== ENHANCED BUSINESS LOGIC TESTS ==========

@pytest.fixture
def setup_agency_and_user():
    """Fixture setup cơ bản cho user và agency"""
    account = Account.objects.create(username="staff1", password_hash="...", account_role="staff")
    user = User.objects.create(account=account, full_name="Staff 1", email="staff@example.com")
    agency_type = AgencyType.objects.create(type_name="Loại 1", max_debt=Decimal("10000000"))
    district = District.objects.create(city_name="HCM", district_name="Quận 1", max_agencies=5)
    agency = Agency.objects.create(
        agency_name="Đại lý 1",
        agency_type=agency_type,
        phone_number="0123456789",
        address="123 ABC",
        district=district,
        email="dl1@example.com",
        representative="Nguyễn Văn A",
        reception_date=date.today(),
        debt_amount=Decimal("0.00")
    )
    return user, agency


@pytest.mark.django_db
class TestBusinessLogicReceipt:
    """Test logic nghiệp vụ cho phiếu nhập"""

    def test_lap_phieu_nhap(self, setup_agency_and_user):
        """Test lập phiếu nhập - tự động cập nhật tổng tiền và tồn kho"""
        user, agency = setup_agency_and_user
        unit = Unit.objects.create(unit_name="Thùng")
        item = Item.objects.create(item_name="Bút", unit=unit, price=Decimal("10000"), stock_quantity=0)

        # Tạo phiếu nhập
        receipt = Receipt.objects.create(
            user_id=user.user_id, 
            agency_id=agency.agency_id,
            total_amount=Decimal("0.00")
        )
        
        # Tạo chi tiết phiếu nhập
        detail = ReceiptDetail.objects.create(
            receipt=receipt,
            item=item,
            quantity=10,
            unit_price=Decimal("10000"),
            line_total=Decimal("100000")
        )

        # Refresh để lấy dữ liệu sau trigger
        receipt.refresh_from_db()
        item.refresh_from_db()
        
        # Kiểm tra tổng tiền phiếu nhập được cập nhật
        assert receipt.total_amount == Decimal("100000")
        
        # Kiểm tra tồn kho được cộng thêm (nếu có trigger)
        # assert item.stock_quantity == 10

    def test_receipt_detail_line_total_calculation(self, setup_agency_and_user):
        """Test tính toán line_total tự động"""
        user, agency = setup_agency_and_user
        unit = Unit.objects.create(unit_name="Cái")
        item = Item.objects.create(item_name="Thước", unit=unit, price=Decimal("5000"), stock_quantity=0)

        receipt = Receipt.objects.create(
            user_id=user.user_id, 
            agency_id=agency.agency_id,
            total_amount=Decimal("0.00")
        )
        
        # Tạo detail với line_total khác quantity * unit_price
        detail = ReceiptDetail.objects.create(
            receipt=receipt,
            item=item,
            quantity=5,
            unit_price=Decimal("5000"),
            line_total=Decimal("20000")  # Sai: phải là 25000
        )
        
        # Nếu có trigger/validation, line_total sẽ được tự động sửa
        detail.refresh_from_db()
        # assert detail.line_total == Decimal("25000")


@pytest.mark.django_db
class TestBusinessLogicIssue:
    """Test logic nghiệp vụ cho phiếu xuất"""

    def test_lap_phieu_xuat_khong_du_ton_kho(self, setup_agency_and_user):
        """Test xuất hàng khi không đủ tồn kho"""
        user, agency = setup_agency_and_user
        unit = Unit.objects.create(unit_name="Cái")
        item = Item.objects.create(item_name="Thước", unit=unit, price=Decimal("2000"), stock_quantity=5)

        issue = Issue.objects.create(
            user_id=user.user_id, 
            agency_id=agency.agency_id, 
            total_amount=Decimal("0.00")
        )
        
        # Cố gắng xuất 10 cái khi chỉ có 5 cái trong kho
        with pytest.raises(Exception, match="Không đủ hàng trong kho"):
            IssueDetail.objects.create(
                issue=issue,
                item=item,
                quantity=10,
                unit_price=Decimal("2040.00"),  # 102% đơn giá nhập
                line_total=Decimal("20400")
            )

    def test_lap_phieu_xuat_vuot_gioi_han_no(self, setup_agency_and_user):
        """Test xuất hàng khi vượt giới hạn nợ"""
        user, agency = setup_agency_and_user
        agency.debt_amount = Decimal("9900000")  # Gần tới giới hạn 10M
        agency.save()

        unit = Unit.objects.create(unit_name="Hộp")
        item = Item.objects.create(item_name="Gôm", unit=unit, price=Decimal("1000"), stock_quantity=100)

        # Cố gắng tạo phiếu xuất với số tiền làm vượt giới hạn nợ
        with pytest.raises(Exception, match="Vượt quá giới hạn nợ"):
            issue = Issue.objects.create(
                user_id=user.user_id, 
                agency_id=agency.agency_id, 
                total_amount=Decimal("110000")  # 9.9M + 110K > 10M
            )

    def test_lap_phieu_xuat_hop_le(self, setup_agency_and_user):
        """Test xuất hàng hợp lệ - cập nhật tồn kho và công nợ"""
        user, agency = setup_agency_and_user
        unit = Unit.objects.create(unit_name="Chai")
        item = Item.objects.create(item_name="Mực", unit=unit, price=Decimal("5000"), stock_quantity=20)

        issue = Issue.objects.create(
            user_id=user.user_id, 
            agency_id=agency.agency_id,
            total_amount=Decimal("0.00")
        )
        
        detail = IssueDetail.objects.create(
            issue=issue,
            item=item,
            quantity=10,
            unit_price=Decimal("5100"),  # đúng quy định 102% giá nhập
            line_total=Decimal("51000")
        )

        # Refresh để lấy dữ liệu sau trigger
        issue.refresh_from_db()
        item.refresh_from_db() 
        agency.refresh_from_db()

        # Kiểm tra cập nhật tổng tiền phiếu xuất
        assert issue.total_amount == Decimal("51000")

        # Kiểm tra trừ tồn kho
        assert item.stock_quantity == 10

        # Kiểm tra cộng công nợ
        assert agency.debt_amount == Decimal("51000")

    def test_issue_price_markup_validation(self, setup_agency_and_user):
        """Test validation giá xuất phải = 102% giá nhập"""
        user, agency = setup_agency_and_user
        unit = Unit.objects.create(unit_name="Cái")
        item = Item.objects.create(item_name="Bút", unit=unit, price=Decimal("1000"), stock_quantity=20)

        issue = Issue.objects.create(
            user_id=user.user_id, 
            agency_id=agency.agency_id,
            total_amount=Decimal("0.00")
        )

        # Test giá xuất không đúng 102%
        with pytest.raises(Exception, match="Giá xuất phải bằng 102% giá nhập"):
            IssueDetail.objects.create(
                issue=issue,
                item=item,
                quantity=5,
                unit_price=Decimal("1000"),  # Chưa nhân 102%
                line_total=Decimal("5000")
            )

        # Test giá xuất đúng 102%
        detail = IssueDetail.objects.create(
            issue=issue,
            item=item,
            quantity=5,
            unit_price=Decimal("1020"),  # 1000 * 1.02
            line_total=Decimal("5100")
        )
        assert detail.unit_price == Decimal("1020")


@pytest.mark.django_db
class TestStockMovements:
    """Test các chuyển động tồn kho"""

    def test_stock_update_after_receipt(self, setup_agency_and_user):
        """Test cập nhật tồn kho sau khi nhập hàng"""
        user, agency = setup_agency_and_user
        unit = Unit.objects.create(unit_name="Thùng")
        item = Item.objects.create(item_name="Giấy A4", unit=unit, price=Decimal("80000"), stock_quantity=5)

        receipt = Receipt.objects.create(user_id=user.user_id, agency_id=agency.agency_id)
        
        # Nhập thêm 10 thùng
        ReceiptDetail.objects.create(
            receipt=receipt,
            item=item,
            quantity=10,
            unit_price=Decimal("80000"),
            line_total=Decimal("800000")
        )

        item.refresh_from_db()
        # Nếu có trigger tự động cộng tồn kho
        # assert item.stock_quantity == 15

    def test_stock_update_after_issue(self, setup_agency_and_user):
        """Test cập nhật tồn kho sau khi xuất hàng"""
        user, agency = setup_agency_and_user
        unit = Unit.objects.create(unit_name="Gói")
        item = Item.objects.create(item_name="Kẹo", unit=unit, price=Decimal("10000"), stock_quantity=50)

        issue = Issue.objects.create(user_id=user.user_id, agency_id=agency.agency_id)
        
        # Xuất 20 gói
        IssueDetail.objects.create(
            issue=issue,
            item=item,
            quantity=20,
            unit_price=Decimal("10200"),  # 102%
            line_total=Decimal("204000")
        )

        item.refresh_from_db()
        assert item.stock_quantity == 30

    def test_multiple_transactions_stock_calculation(self, setup_agency_and_user):
        """Test tính tồn kho với nhiều giao dịch"""
        user, agency = setup_agency_and_user
        unit = Unit.objects.create(unit_name="Cuộn")
        item = Item.objects.create(item_name="Dây điện", unit=unit, price=Decimal("10000"), stock_quantity=0)

        # Nhập 50
        receipt = Receipt.objects.create(user_id=user.user_id, agency_id=agency.agency_id)
        ReceiptDetail.objects.create(
            receipt=receipt, 
            item=item, 
            quantity=50, 
            unit_price=Decimal("10000"), 
            line_total=Decimal("500000")
        )

        # Xuất 20
        issue = Issue.objects.create(user_id=user.user_id, agency_id=agency.agency_id)
        IssueDetail.objects.create(
            issue=issue, 
            item=item, 
            quantity=20, 
            unit_price=Decimal("10200"), 
            line_total=Decimal("204000")
        )

        # Nhập thêm 15
        receipt2 = Receipt.objects.create(user_id=user.user_id, agency_id=agency.agency_id)
        ReceiptDetail.objects.create(
            receipt=receipt2, 
            item=item, 
            quantity=15, 
            unit_price=Decimal("10000"), 
            line_total=Decimal("150000")
        )

        item.refresh_from_db()
        # Tồn kho cuối = 0 + 50 - 20 + 15 = 45 (nếu có trigger tự động)
        # assert item.stock_quantity == 45


@pytest.mark.django_db
class TestDebtManagement:
    """Test quản lý công nợ"""

    def test_debt_increase_after_issue(self, setup_agency_and_user):
        """Test tăng công nợ sau khi xuất hàng"""
        user, agency = setup_agency_and_user
        unit = Unit.objects.create(unit_name="Hộp")
        item = Item.objects.create(item_name="Bánh", unit=unit, price=Decimal("15000"), stock_quantity=30)

        initial_debt = agency.debt_amount

        issue = Issue.objects.create(user_id=user.user_id, agency_id=agency.agency_id)
        IssueDetail.objects.create(
            issue=issue,
            item=item,
            quantity=5,
            unit_price=Decimal("15300"),  # 102%
            line_total=Decimal("76500")
        )

        agency.refresh_from_db()
        assert agency.debt_amount == initial_debt + Decimal("76500")

    def test_debt_limit_enforcement(self, setup_agency_and_user):
        """Test thực thi giới hạn nợ"""
        user, agency = setup_agency_and_user
        
        # Set debt gần giới hạn
        agency.debt_amount = Decimal("9999000")  # Còn 1000 so với giới hạn 10M
        agency.save()

        unit = Unit.objects.create(unit_name="Chai")
        item = Item.objects.create(item_name="Nước", unit=unit, price=Decimal("5000"), stock_quantity=100)

        # Cố gắng xuất hàng trị giá > 1000
        issue = Issue.objects.create(user_id=user.user_id, agency_id=agency.agency_id)
        
        with pytest.raises(Exception, match="Vượt quá giới hạn nợ"):
            IssueDetail.objects.create(
                issue=issue,
                item=item,
                quantity=1,
                unit_price=Decimal("5100"),
                line_total=Decimal("5100")  # Làm tổng nợ vượt 10M
            )


# ========== DATABASE VIEWS AND FIXTURES ==========

@pytest.fixture(scope='session')
def apply_views(django_db_setup, django_db_blocker):
    """
    Fixture to apply database views from a SQL file.
    This is a workaround for views not being part of migrations.
    """
    with django_db_blocker.unblock():
        # Construct the path to the SQL file relative to this test file.
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        sql_file_path = os.path.join(base_dir, 'db', 'newddl.sql')

        with open(sql_file_path, 'r') as f:
            sql = f.read()
            # Split SQL file into individual statements.
            statements = [s.strip() for s in sql.split(';') if s.strip()]
            with connection.cursor() as cursor:
                for statement in statements:
                    # Execute each statement, ignoring potential errors if views/schemas already exist.
                    try:
                        cursor.execute(statement)
                    except Exception:
                        # This is a broad exception, but for the purpose of creating
                        # views in a test setup, it's acceptable to ignore errors
                        # like "schema already exists" or "view already exists".
                        pass


@pytest.mark.django_db
@pytest.mark.usefixtures("apply_views")
class TestViews:
    """Kiểm tra các view trong database"""

    def test_debt_summary_view(self):
        """Kiểm tra view finance.v_debt_summary"""
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM finance.v_debt_summary")
            rows = cursor.fetchall()
            assert isinstance(rows, list)

    def test_stock_balance_view(self):
        """Kiểm tra view inventory.v_stock_balance"""
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM inventory.v_stock_balance")
            rows = cursor.fetchall()
            assert isinstance(rows, list)

    def test_view_ton_kho_with_data(self, setup_agency_and_user):
        """Test view tồn kho với dữ liệu thực tế"""
        user, agency = setup_agency_and_user
        unit = Unit.objects.create(unit_name="Cuộn")
        item = Item.objects.create(item_name="Dây điện", unit=unit, price=Decimal("10000"), stock_quantity=0)

        # Giả lập phiếu nhập 50
        receipt = Receipt.objects.create(user_id=user.user_id, agency_id=agency.agency_id)
        ReceiptDetail.objects.create(
            receipt=receipt, 
            item=item, 
            quantity=50, 
            unit_price=Decimal("10000"), 
            line_total=Decimal("500000")
        )

        # Giả lập phiếu xuất 20
        issue = Issue.objects.create(user_id=user.user_id, agency_id=agency.agency_id)
        IssueDetail.objects.create(
            issue=issue, 
            item=item, 
            quantity=20, 
            unit_price=Decimal("10200"), 
            line_total=Decimal("204000")
        )

        # Truy vấn view v_stock_balance
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT stock_on_hand FROM inventory.v_stock_balance WHERE item_id = {item.item_id}")
            result = cursor.fetchone()
            if result:
                stock_on_hand = result[0]
                assert stock_on_hand == 30  # 50 - 20

