from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum
from django.utils.timezone import now
from datetime import timedelta

from apps.inventory.models import Issue, Receipt
from apps.finance.models import Payment
from apps.agencies.models import Agency
from apps.accounts.permissions import IsAdminOrDistributor


class DashboardOverviewAPIView(APIView):
    """
    Tổng quan dashboard: tổng số đơn xuất, nhập, tổng tiền thu, công nợ
    """
    permission_classes = [IsAuthenticated, IsAdminOrDistributor]

    def get(self, request):
        today = now().date()
        week_ago = today - timedelta(days=7)

        data = {
            "total_issues": Issue.objects.count(),
            "total_receipts": Receipt.objects.count(),
            "total_payments": Payment.objects.aggregate(total=Sum("amount_collected"))["total"] or 0,
            "total_debt": Agency.objects.aggregate(total=Sum("debt"))["total"] or 0,
            "weekly_issues": Issue.objects.filter(issue_date__gte=week_ago).count(),
            "weekly_receipts": Receipt.objects.filter(receipt_date__gte=week_ago).count(),
        }
        return Response(data)


class SalesChartAPIView(APIView):
    """
    Trả về số đơn xuất hàng theo ngày trong 7 ngày gần nhất
    """
    permission_classes = [IsAuthenticated, IsAdminOrDistributor]

    def get(self, request):
        today = now().date()
        data = []
        for i in range(7):
            day = today - timedelta(days=i)
            count = Issue.objects.filter(issue_date=day).count()
            data.append({"date": str(day), "issues": count})
        return Response(list(reversed(data)))
