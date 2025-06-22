from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PaymentViewSet, ReportViewSet, DebtViewSet

# Create router for ViewSets
router = DefaultRouter()
router.register(r'payments', PaymentViewSet, basename='payment')
router.register(r'reports', ReportViewSet, basename='report')
router.register(r'debts', DebtViewSet, basename='debt')

urlpatterns = [
    # Finance API endpoints
    # Following docs/api.md structure:
    # GET/POST     /api/v1/finance/payments/
    # GET          /api/v1/finance/payments/{id}/
    # GET/POST     /api/v1/finance/reports/
    # GET          /api/v1/finance/reports/{id}/
    # GET          /api/v1/finance/debts/
    # GET          /api/v1/finance/debts/summary/
    # GET          /api/v1/finance/debts/aging/
    path('', include(router.urls)),
] 