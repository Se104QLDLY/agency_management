from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PaymentViewSet, PaymentExcelReportView, DebtPDFReportView


router = DefaultRouter()
router.register(r'payments', PaymentViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('reports/excel/', PaymentExcelReportView.as_view(), name='report-excel'),
    path('reports/debt-pdf/', DebtPDFReportView.as_view(), name='report-debt-pdf'),
]
