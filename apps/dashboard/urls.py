from django.urls import path
from .views import (
    DashboardOverviewAPIView,
    SalesReportAPIView,
    StockReportAPIView,
    DebtReportAPIView,
)

urlpatterns = [
    path('overview/', DashboardOverviewAPIView.as_view(), name='dashboard-overview'),
    path('reports/sales/', SalesReportAPIView.as_view(), name='sales-report'),
    path('reports/stock/', StockReportAPIView.as_view(), name='stock-report'),
    path('reports/debts/', DebtReportAPIView.as_view(), name='debt-report'),
]
