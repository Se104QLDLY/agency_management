from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PaymentViewSet,
    PaymentExcelReportView,
    DebtPDFReportView
)

router = DefaultRouter()
router.register(r'payments', PaymentViewSet, basename='payments')

urlpatterns = [
    path('', include(router.urls)),
    path('report/payment-excel/', PaymentExcelReportView.as_view(), name='payment-excel'),
    path('report/debt-pdf/', DebtPDFReportView.as_view(), name='debt-pdf'),
]
