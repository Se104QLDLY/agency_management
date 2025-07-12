# managers.py
from django.db import models
from django.utils import timezone
from django.apps import apps
from django.db.models import Sum, Count
from decimal import Decimal

class ReportManager(models.Manager):
    def create_debt_report(self, for_date, created_by, agency_id=None, start_date=None, end_date=None):
        """
        Tạo báo cáo công nợ đơn giản: Mã đại lý, Tên đại lý, Phát sinh, Thanh toán
        Chỉ tính Issue có status='delivered' và Payment có status='completed'
        """
        Agency = apps.get_model('agency', 'Agency')
        Issue = apps.get_model('inventory', 'Issue')
        Payment = apps.get_model('finance', 'Payment')
        
        # Lấy danh sách đại lý
        if agency_id:
            agencies = Agency.objects.filter(agency_id=agency_id)
        else:
            agencies = Agency.objects.all()
        
        debt_summary = []
        
        for agency in agencies:
            # Phát sinh nợ trong kỳ (từ các phiếu xuất có status='delivered')
            if start_date and end_date:
                issues_in_period = Issue.objects.filter(
                    agency_id=agency.agency_id,
                    issue_date__gte=start_date,
                    issue_date__lte=end_date,
                    status='delivered'  # Chỉ tính phiếu đã giao hàng
                ).aggregate(total=Sum('total_amount'))
            else:
                issues_in_period = Issue.objects.filter(
                    agency_id=agency.agency_id,
                    issue_date__year=for_date.year,
                    issue_date__month=for_date.month,
                    status='delivered'  # Chỉ tính phiếu đã giao hàng
                ).aggregate(total=Sum('total_amount'))
            
            debt_incurred = issues_in_period['total'] or Decimal('0')
            
            # Thanh toán trong kỳ (chỉ tính payment có status='completed')
            if start_date and end_date:
                payments_in_period = Payment.objects.filter(
                    agency_id=agency.agency_id,
                    payment_date__gte=start_date,
                    payment_date__lte=end_date,
                    status='completed'  # Chỉ tính thanh toán đã hoàn thành
                ).aggregate(total=Sum('amount_collected'))
            else:
                payments_in_period = Payment.objects.filter(
                    agency_id=agency.agency_id,
                    payment_date__year=for_date.year,
                    payment_date__month=for_date.month,
                    status='completed'  # Chỉ tính thanh toán đã hoàn thành
                ).aggregate(total=Sum('amount_collected'))
            
            debt_paid = payments_in_period['total'] or Decimal('0')
            
            debt_summary.append({
                'agency_id': agency.agency_id,
                'agency_name': agency.agency_name,
                'debt_incurred': float(debt_incurred),
                'debt_paid': float(debt_paid)
            })
        
        return self.create(
            report_type='debt',
            report_date=for_date,
            data={'summary': debt_summary},
            created_by=created_by
        )

    def create_sales_report(self, for_month, created_by, agency_id=None):
        """
        Tạo báo cáo doanh số theo tháng
        """
        Issue = apps.get_model('inventory', 'Issue')
        Agency = apps.get_model('agency', 'Agency')
        
        # Lấy dữ liệu doanh số
        sales_query = Issue.objects.filter(
            issue_date__year=for_month.year,
            issue_date__month=for_month.month
        )
        
        if agency_id:
            sales_query = sales_query.filter(agency_id=agency_id)
        
        sales_data = sales_query.values('agency_id').annotate(
            total_sales=Sum('total_amount'),
            total_issues=Count('issue_id')
        ).order_by('-total_sales')
        
        # Get agency names
        agency_ids = [item['agency_id'] for item in sales_data]
        agencies = {agency.agency_id: agency.agency_name for agency in Agency.objects.filter(agency_id__in=agency_ids)}
        
        # Add agency names to sales data
        for item in sales_data:
            item['agency_name'] = agencies.get(item['agency_id'], 'Unknown Agency')
        
        return self.create(
            report_type='sales',
            report_date=for_month,
            data={'sales': list(sales_data)},
            created_by=created_by
        )

    def create_inventory_report(self, for_date, created_by):
        """
        Tạo báo cáo tồn kho - chỉ hiển thị items có số lượng tồn kho > 0
        """
        Item = apps.get_model('inventory', 'Item')
        
        # Lấy items có tồn kho > 0
        items_with_stock = Item.objects.filter(
            stock_quantity__gt=0
        ).select_related('unit').values(
            'item_id',
            'item_name',
            'unit__unit_name',
            'stock_quantity',
            'price'
        )
        
        inventory_data = []
        total_value = Decimal('0')
        
        for item in items_with_stock:
            item_total = (item['stock_quantity'] or 0) * (item['price'] or Decimal('0'))
            total_value += item_total
            
            inventory_data.append({
                'item_id': item['item_id'],
                'item_name': item['item_name'],
                'unit_name': item['unit__unit_name'],
                'stock_quantity': item['stock_quantity'],
                'price': float(item['price'] or Decimal('0')),
                'total_value': float(item_total)
            })
        
        return self.create(
            report_type='inventory',
            report_date=for_date,
            data={
                'items': inventory_data,
                'total_items': len(inventory_data),
                'total_value': float(total_value)
            },
            created_by=created_by
        )