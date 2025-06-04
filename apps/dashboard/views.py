from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.inventory.models import Item, Issue, Receipt
from apps.finance.models import Payment
from apps.agencies.models import Agency
from django.db.models import Sum
from .permissions import IsAdminOrDistributor, IsAllRoles

class DashboardOverviewAPIView(APIView):
    """
    Dashboard tổng quan nhập/xuất, thanh toán (chỉ A1, A2)
    """
    permission_classes = [IsAuthenticated, IsAdminOrDistributor]

    def get(self, request):
        total_items = Item.objects.count()
        total_issues = Issue.objects.count()
        total_receipts = Receipt.objects.count()
        total_payments = Payment.objects.aggregate(total=Sum("amount_collected"))["total"] or 0

        return Response({
            "total_items": total_items,
            "total_issues": total_issues,
            "total_receipts": total_receipts,
            "total_collected": total_payments
        })


class SalesReportAPIView(APIView):
    """
    Lập báo cáo doanh thu (A1, A2, A3)
    """
    permission_classes = [IsAuthenticated, IsAllRoles]

    def get(self, request):
        payments_by_agency = (
            Payment.objects
            .values('agency__name')
            .annotate(total_collected=Sum('amount_collected'))
            .order_by('-total_collected')
        )
        return Response(list(payments_by_agency))


class StockReportAPIView(APIView):
    """
    Báo cáo tồn kho theo mặt hàng
    """
    permission_classes = [IsAuthenticated, IsAllRoles]

    def get(self, request):
        stock = Item.objects.values('name', 'stock_quantity')
        return Response(list(stock))


class DebtReportAPIView(APIView):
    """
    Báo cáo công nợ theo đại lý
    """
    permission_classes = [IsAuthenticated, IsAllRoles]

    def get(self, request):
        debts = Agency.objects.values('name', 'debt').order_by('-debt')
        return Response(list(debts))
