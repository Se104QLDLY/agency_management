from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count
from datetime import datetime
from apps.inventory.models import Issue
from apps.finance.models import Payment
from apps.agencies.models import Agency
from django.db.models.functions import TruncMonth


class DashboardOverviewAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        total_agencies = Agency.objects.count()
        total_debt = Agency.objects.aggregate(total_debt=Sum('debt'))['total_debt'] or 0

        current_month = datetime.now().month
        current_year = datetime.now().year

        total_sales = (
            Issue.objects.filter(issue_date__month=current_month, issue_date__year=current_year)
            .aggregate(total=Sum('total_amount'))['total'] or 0
        )

        top_debtors = (
            Agency.objects.order_by('-debt')[:5]
            .values('name', 'debt', 'agency_type__type_name')
        )

        return Response({
            'total_agencies': total_agencies,
            'total_debt': total_debt,
            'total_sales': total_sales,
            'top_debtors': top_debtors
        })


class SalesChartAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        sales_by_month = (
            Issue.objects
            .annotate(month=TruncMonth('issue_date'))
            .values('month')
            .annotate(total=Sum('total_amount'))
            .order_by('month')
        )
        return Response(sales_by_month)
