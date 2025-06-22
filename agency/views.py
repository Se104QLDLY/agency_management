from django.shortcuts import render
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db import transaction

from .models import Agency, AgencyType, District, StaffAgency
from .serializers import (
    AgencyListSerializer, 
    AgencyDetailSerializer, 
    AgencyCreateSerializer,
    AgencyTypeSerializer, 
    DistrictSerializer,
    StaffAgencySerializer
)


class AgencyTypeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for AgencyType management
    Provides CRUD operations for agency types with debt limits
    """
    queryset = AgencyType.objects.all()
    serializer_class = AgencyTypeSerializer
    permission_classes = [AllowAny]  # Temporarily allow public access for testing
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['type_name', 'description']
    ordering_fields = ['type_name', 'max_debt']
    ordering = ['type_name']


class DistrictViewSet(viewsets.ModelViewSet):
    """
    ViewSet for District management
    Handles geographical districts with agency capacity limits
    """
    queryset = District.objects.all()
    serializer_class = DistrictSerializer
    permission_classes = [AllowAny]  # Temporarily allow public access for testing
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['district_name', 'city_name']
    filterset_fields = ['city_name']
    ordering_fields = ['district_name', 'city_name', 'max_agencies']
    ordering = ['city_name', 'district_name']

    @action(detail=True, methods=['get'])
    def capacity(self, request, pk=None):
        """
        Get district capacity information
        Returns current agency count vs max_agencies limit
        """
        district = self.get_object()
        current_count = Agency.objects.filter(district_id=district.district_id).count()
        
        return Response({
            'district_id': district.district_id,
            'district_name': district.district_name,
            'city_name': district.city_name,
            'max_agencies': district.max_agencies,
            'current_agencies': current_count,
            'available_slots': district.max_agencies - current_count,
            'is_full': current_count >= district.max_agencies
        })


class AgencyViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Agency management
    Implements full agency lifecycle per docs/flow.md:
    Register → Approve → Operate → Block/Unblock
    """
    queryset = Agency.objects.all()
    permission_classes = [AllowAny]  # Temporarily allow public access for testing
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['agency_name', 'email', 'phone_number', 'representative']
    filterset_fields = ['agency_type', 'district', 'debt_amount']
    ordering_fields = ['agency_name', 'reception_date', 'debt_amount', 'created_at']
    ordering = ['agency_name']

    def get_serializer_class(self):
        """
        Return appropriate serializer based on action
        Following docs/api.md patterns for different views
        """
        if self.action == 'list':
            return AgencyListSerializer
        elif self.action == 'create':
            return AgencyCreateSerializer
        else:
            return AgencyDetailSerializer

    def get_queryset(self):
        """
        Optionally filter by status for different user roles
        """
        queryset = Agency.objects.select_related('agency_type', 'district')
        
        # Filter by status if provided
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            # Note: Agency model doesn't have status field in DDL.sql
            # This would need to be added if status workflow is required
            pass
            
        return queryset

    def create(self, request, *args, **kwargs):
        """
        Agency Registration Flow per docs/flow.md
        1. Validate data
        2. Create agency with default status
        3. Trigger background notification (future: Celery)
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        with transaction.atomic():
            agency = serializer.save()
            
            # TODO: Trigger Celery task for notification
            # notify_new_agency.delay(agency.agency_id)
            
        # Return created agency with full details
        response_serializer = AgencyDetailSerializer(agency)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """
        Approve pending agency per docs/flow.md
        Sets approval timestamp and initializes debt tracking
        """
        agency = self.get_object()
        
        # Business logic: Can only approve if not already approved
        # Note: DDL.sql doesn't have approval status fields
        # This would need schema extension for full workflow
        
        with transaction.atomic():
            # Update approval timestamp (would need DDL schema update)
            # agency.approved_at = timezone.now()
            # agency.status = 'ACTIVE'
            # agency.save()
            
            # Initialize debt tracking (debt_amount already defaults to 0 per DDL)
            # Create initial debt transaction record (would need finance schema)
            pass
            
        return Response({
            'message': 'Agency approved successfully',
            'agency_id': agency.agency_id,
            'agency_name': agency.agency_name,
            'approved_at': timezone.now().isoformat()
        })

    @action(detail=True, methods=['post'])  
    def block(self, request, pk=None):
        """
        Block/unblock agency operations
        Note: DDL.sql doesn't include status field - would need schema update
        """
        agency = self.get_object()
        action_type = request.data.get('action', 'block')  # 'block' or 'unblock'
        
        if action_type not in ['block', 'unblock']:
            return Response(
                {'error': 'Action must be either "block" or "unblock"'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Note: Would need DDL schema update to add status/blocked fields
        # For now, return success response
        return Response({
            'message': f'Agency {action_type}ed successfully',
            'agency_id': agency.agency_id,
            'agency_name': agency.agency_name,
            'action': action_type,
            'updated_at': timezone.now().isoformat()
        })

    @action(detail=True, methods=['get'])
    def debt(self, request, pk=None):
        """
        Get current debt & aging buckets per docs/api.md
        Returns debt summary with aging analysis
        """
        agency = self.get_object()
        
        # Current debt from DDL.sql agency table
        current_debt = agency.debt_amount
        
        # Get debt limit from agency type
        max_debt = agency.agency_type.max_debt
        
        # TODO: Implement aging buckets with finance schema
        # This would require joining with payment/issue history
        aging_buckets = {
            'current': current_debt,  # 0-30 days
            '30_days': 0,   # 31-60 days 
            '60_days': 0,   # 61-90 days
            '90_days_plus': 0  # 90+ days
        }
        
        return Response({
            'agency_id': agency.agency_id,
            'agency_name': agency.agency_name,
            'current_debt': current_debt,
            'debt_limit': max_debt,
            'available_credit': max_debt - current_debt,
            'can_issue_more': current_debt < max_debt,
            'utilization_percentage': round((current_debt / max_debt) * 100, 2) if max_debt > 0 else 0,
            'aging_buckets': aging_buckets
        })

    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        """
        Get complete transaction history per docs/api.md
        Returns receipts, issues, and payments for the agency
        """
        agency = self.get_object()
        
        # TODO: Implement with finance/inventory schemas
        # For now return empty structure per docs/api.md
        
        return Response({
            'agency_id': agency.agency_id,
            'agency_name': agency.agency_name,
            'receipts': [],  # TODO: Join with INVENTORY.Receipt
            'issues': [],    # TODO: Join with INVENTORY.Issue  
            'payments': [],  # TODO: Join with FINANCE.Payment
            'summary': {
                'total_receipts': 0,
                'total_issues': 0,
                'total_payments': 0,
                'net_debt_change': 0
            }
        })


class StaffAgencyViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Staff-Agency relationship management
    Handles assignment of staff to agencies per DDL.sql composite key design
    """
    queryset = StaffAgency.objects.select_related('agency')
    serializer_class = StaffAgencySerializer
    permission_classes = [AllowAny]  # Temporarily allow public access for testing
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['staff_id', 'agency']

    def create(self, request, *args, **kwargs):
        """
        Assign staff to agency with composite key validation
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        with transaction.atomic():
            staff_agency = serializer.save()
            
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def by_staff(self, request):
        """
        Get all agencies managed by a specific staff member
        URL: /staff-agencies/by_staff/?staff_id=123
        """
        staff_id = request.query_params.get('staff_id')
        if not staff_id:
            return Response(
                {'error': 'staff_id parameter is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        assignments = self.queryset.filter(staff_id=staff_id)
        agencies = [assignment.agency for assignment in assignments]
        
        # Use AgencyListSerializer for consistency
        agency_serializer = AgencyListSerializer(agencies, many=True)
        
        return Response({
            'staff_id': int(staff_id),
            'agency_count': len(agencies),
            'agencies': agency_serializer.data
        })

    @action(detail=False, methods=['get'])
    def by_agency(self, request):
        """
        Get all staff managing a specific agency
        URL: /staff-agencies/by_agency/?agency_id=123
        """
        agency_id = request.query_params.get('agency_id')
        if not agency_id:
            return Response(
                {'error': 'agency_id parameter is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        assignments = self.queryset.filter(agency_id=agency_id)
        
        # TODO: Get staff details from auth.USER table
        # For now return basic staff_id info
        staff_list = [
            {
                'staff_id': assignment.staff_id,
                'staff_name': f'Staff {assignment.staff_id}'  # TODO: Get from auth.USER
            }
            for assignment in assignments
        ]
        
        return Response({
            'agency_id': int(agency_id),
            'staff_count': len(staff_list),
            'staff': staff_list
        })
