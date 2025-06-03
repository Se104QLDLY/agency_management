from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UnitViewSet, ItemViewSet,
    ReceiptViewSet, ReceiptDetailViewSet,
    IssueViewSet, IssueDetailViewSet
)

router = DefaultRouter()
router.register(r'units', UnitViewSet, basename='unit')                     # A1, A2: Quản lý đơn vị tính
router.register(r'items', ItemViewSet, basename='item')                     # A1, A2: Quản lý mặt hàng
router.register(r'receipts', ReceiptViewSet, basename='receipt')           # A1, A2, A3: Quản lý nhập hàng
router.register(r'receipt-details', ReceiptDetailViewSet, basename='receipt-detail')  # Chi tiết nhập
router.register(r'issues', IssueViewSet, basename='issue')                 # A1, A2: Quản lý xuất hàng
router.register(r'issue-details', IssueDetailViewSet, basename='issue-detail')        # Chi tiết xuất

urlpatterns = [
    path('', include(router.urls)),
]
