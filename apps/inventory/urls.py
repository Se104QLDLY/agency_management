from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UnitViewSet, ItemViewSet,
    ReceiptViewSet, ReceiptDetailViewSet,
    IssueViewSet, IssueDetailViewSet
)

router = DefaultRouter()
router.register(r'units', UnitViewSet)
router.register(r'items', ItemViewSet)
router.register(r'receipts', ReceiptViewSet)
router.register(r'receipt-details', ReceiptDetailViewSet)
router.register(r'issues', IssueViewSet)
router.register(r'issue-details', IssueDetailViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
