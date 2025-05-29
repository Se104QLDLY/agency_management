from django.urls import path
from .views import DashboardOverviewAPIView, SalesChartAPIView

urlpatterns = [
    path('overview/', DashboardOverviewAPIView.as_view(), name='dashboard-overview'),
    path('sales-chart/', SalesChartAPIView.as_view(), name='dashboard-sales-chart'),
]
