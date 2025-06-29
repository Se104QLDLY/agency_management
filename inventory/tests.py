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


@pytest.fixture(scope='session')
def apply_views(django_db_setup, django_db_blocker):
    """
    Fixture to apply database views from a SQL file.
    This is a workaround for views not being part of migrations.
    """
    with django_db_blocker.unblock():
        # Construct the path to the SQL file relative to this test file.
        # __file__ is the path to the current file (tests.py)
        # os.path.dirname gives the directory of the file.
        # os.path.join is used to safely join path components.
        # Correctly locate the 'db/newddl.sql' file from the project root.
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        sql_file_path = os.path.join(base_dir, 'db', 'newddl.sql')

        with open(sql_file_path, 'r') as f:
            sql = f.read()
            # Split SQL file into individual statements.
            # This is a simple split, might need adjustment for complex SQL.
            statements = [s.strip() for s in sql.split(';') if s.strip()]
            with connection.cursor() as cursor:
                for statement in statements:
                    # Execute each statement, ignoring potential errors if views/schemas already exist.
                    # This makes the fixture runnable multiple times without failure.
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