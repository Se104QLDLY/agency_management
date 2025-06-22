from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UnitViewSet, ItemViewSet, ReceiptViewSet, IssueViewSet

# Create router for ViewSets
router = DefaultRouter()
router.register(r'units', UnitViewSet, basename='unit')
router.register(r'items', ItemViewSet, basename='item')
router.register(r'receipts', ReceiptViewSet, basename='receipt')
router.register(r'issues', IssueViewSet, basename='issue')

urlpatterns = [
    # Inventory API endpoints
    # Following docs/api.md structure:
    # GET/POST     /api/v1/inventory/items/
    # GET/PUT/PATCH/DELETE /api/v1/inventory/items/{id}/
    # GET/POST     /api/v1/inventory/receipts/
    # GET          /api/v1/inventory/receipts/{id}/
    # GET/POST     /api/v1/inventory/issues/
    # GET          /api/v1/inventory/issues/{id}/
    path('', include(router.urls)),
] 