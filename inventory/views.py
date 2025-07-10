from django.shortcuts import render
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from .models import Unit, Item, Receipt, Issue
from .serializers import (
    UnitSerializer,
    ItemListSerializer, ItemDetailSerializer, ItemCreateUpdateSerializer,
    ReceiptListSerializer, ReceiptDetailNestedSerializer, ReceiptCreateSerializer,
    ReceiptStatusUpdateSerializer,
    IssueListSerializer, IssueDetailNestedSerializer, IssueCreateSerializer,
    IssueStatusUpdateSerializer
)
from authentication.permissions import CookieJWTAuthentication, InventoryPermission
from .services import InventoryService
from authentication.exceptions import DebtLimitExceeded, OutOfStock


class UnitViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing inventory units
    """
    queryset = Unit.objects.all()
    serializer_class = UnitSerializer
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [InventoryPermission]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['unit_name']
    ordering_fields = ['unit_name']
    ordering = ['unit_name']


class ItemViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing inventory items
    GET /api/v1/inventory/items/ - List items with search
    POST /api/v1/inventory/items/ - Create new item
    GET /api/v1/inventory/items/{id}/ - Item detail
    PATCH /api/v1/inventory/items/{id}/ - Update item
    DELETE /api/v1/inventory/items/{id}/ - Soft delete item
    """
    queryset = Item.objects.all()
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [InventoryPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['unit', 'stock_quantity']
    search_fields = ['item_name', 'description']
    ordering_fields = ['item_name', 'price', 'stock_quantity']
    ordering = ['item_name']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ItemListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ItemCreateUpdateSerializer
        else:
            return ItemDetailSerializer
    
    def get_queryset(self):
        queryset = Item.objects.select_related('unit')
        
        # Filter by stock level
        low_stock = self.request.query_params.get('low_stock')
        if low_stock:
            try:
                threshold = int(low_stock)
                queryset = queryset.filter(stock_quantity__lt=threshold)
            except ValueError:
                pass
                
        return queryset
    
    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        """Get items with low stock (< 10)"""
        items = self.get_queryset().filter(stock_quantity__lt=10)
        serializer = self.get_serializer(items, many=True)
        return Response(serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        """Soft delete - mark as inactive instead of actual delete"""
        # For now, we'll prevent deletion if item has transactions
        item = self.get_object()
        if item.receipt_details.exists() or item.issue_details.exists():
            return Response(
                {'error': 'Cannot delete item with existing transactions'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().destroy(request, *args, **kwargs)


class ReceiptViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing stock-in receipts
    GET /api/v1/inventory/receipts/ - List receipts with filters
    POST /api/v1/inventory/receipts/ - Create new receipt
    GET /api/v1/inventory/receipts/{id}/ - Receipt detail with items
    """
    queryset = Receipt.objects.all()
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [InventoryPermission]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['agency_id', 'user_id', 'receipt_date']
    ordering_fields = ['receipt_date', 'total_amount', 'created_at']
    ordering = ['-receipt_date']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ReceiptListSerializer
        elif self.action == 'create':
            return ReceiptCreateSerializer
        elif self.action == 'update_status':
            return ReceiptStatusUpdateSerializer
        else:
            return ReceiptDetailNestedSerializer
    
    def get_queryset(self):
        queryset = Receipt.objects.all()
        
        # Date range filtering
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        
        if date_from:
            queryset = queryset.filter(receipt_date__gte=date_from)
        if date_to:
            queryset = queryset.filter(receipt_date__lte=date_to)
            
        return queryset
    
    def create(self, request, *args, **kwargs):
        """Create receipt with items using business logic service"""
        try:
            # Create copy of request data to avoid modifying original
            receipt_data = request.data.copy()
            
            # Always use default distributor agency (ID=5) for receipts
            # Since receipts are stock-in operations, not customer orders
            receipt_data['agency_id'] = 5
            
            receipt = InventoryService.create_receipt(receipt_data, request.user)
            detail_serializer = ReceiptDetailNestedSerializer(receipt)
            return Response(detail_serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['patch'], url_path='status', url_name='update-status')
    def update_status(self, request, pk=None):
        """Update the status of a receipt."""
        receipt = self.get_object()
        serializer = self.get_serializer(receipt, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class IssueViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing stock-out issues
    GET /api/v1/inventory/issues/ - List issues with filters
    POST /api/v1/inventory/issues/ - Create new issue (with debt check)
    GET /api/v1/inventory/issues/{id}/ - Issue detail with debt impact
    """
    queryset = Issue.objects.all()
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [InventoryPermission]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['agency_id', 'user_id', 'issue_date']
    ordering_fields = ['issue_date', 'total_amount', 'created_at']
    ordering = ['-issue_date']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return IssueListSerializer
        elif self.action == 'create':
            return IssueCreateSerializer
        elif self.action == 'update_status':
            return IssueStatusUpdateSerializer
        else:
            return IssueDetailNestedSerializer
    
    def get_queryset(self):
        queryset = Issue.objects.all()
        
        # Date range filtering
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        
        if date_from:
            queryset = queryset.filter(issue_date__gte=date_from)
        if date_to:
            queryset = queryset.filter(issue_date__lte=date_to)
            
        return queryset
    
    def create(self, request, *args, **kwargs):
        """Create issue with stock and debt validation using business logic service"""
        try:
            issue = InventoryService.create_issue(request.data, request.user)
            detail_serializer = IssueDetailNestedSerializer(issue)
            return Response(detail_serializer.data, status=status.HTTP_201_CREATED)
        except (DebtLimitExceeded, OutOfStock) as e:
            # Business rule violations - handled by custom exception handler
            raise
        except Exception as e:
            # Catch any other unexpected errors
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def by_agency(self, request):
        """Get issues for specific agency"""
        agency_id = request.query_params.get('agency_id')
        if not agency_id:
            return Response(
                {'error': 'agency_id parameter required'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        issues = self.get_queryset().filter(agency_id=agency_id)
        serializer = self.get_serializer(issues, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['patch'], url_path='status', url_name='update-status')
    def update_status(self, request, pk=None):
        """
        Update the status of an issue with proper business logic.
        Handles stock validation when approving requests.
        """
        issue = self.get_object()
        new_status = request.data.get('status')
        
        try:
            if new_status == 'confirmed' and issue.status == 'processing':
                # DEBUG: Kiểm tra method của InventoryService
                print('DEBUG InventoryService:', dir(InventoryService))
                # Staff approving a pending request - validate stock and deduct
                InventoryService.approve_issue(issue, request.user)
                serializer = self.get_serializer(issue)
                return Response(serializer.data)
                
            elif new_status == 'cancelled' and issue.status == 'processing':
                # Staff rejecting a pending request
                rejection_reason = request.data.get('status_reason', 'Rejected by staff')
                InventoryService.reject_issue(issue, request.user, rejection_reason)
                serializer = self.get_serializer(issue)
                return Response(serializer.data)
                
            else:
                # Other status updates (use existing serializer)
                serializer = self.get_serializer(issue, data=request.data, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data)
                
        except OutOfStock as e:
            return Response(
                {'error': f'Cannot approve request: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )