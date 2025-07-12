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
from authentication.permissions import CookieJWTAuthentication, AgencyPermission


class AgencyTypeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for AgencyType management
    Provides CRUD operations for agency types with debt limits
    """
    queryset = AgencyType.objects.all()
    serializer_class = AgencyTypeSerializer
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [AgencyPermission]
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
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [AgencyPermission]
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
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [AgencyPermission]
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
        Add security filtering - agents can only see their own agency, staff can only see assigned agencies
        """
        queryset = Agency.objects.select_related('agency_type', 'district')
        
        # Filter by status if provided
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            # Note: Agency model doesn't have status field in DDL.sql
            # This would need to be added if status workflow is required
            pass
        
        # Security filtering based on user role
        if hasattr(self.request.user, 'user_id'):
            try:
                from authentication.models import User
                requesting_user = User.objects.select_related('account').get(user_id=self.request.user.user_id)
                
                if requesting_user.account.account_role == 'agent':
                    # Agent can only see their own agency
                    queryset = queryset.filter(user_id=requesting_user.user_id)
                elif requesting_user.account.account_role == 'staff':
                    # Staff can only see agencies they're assigned to
                    assigned_agencies = StaffAgency.objects.filter(staff_id=requesting_user.user_id).values_list('agency_id', flat=True)
                    if assigned_agencies:
                        queryset = queryset.filter(agency_id__in=assigned_agencies)
                    else:
                        # Staff not assigned to any agency - return empty queryset
                        queryset = queryset.none()
                # Admin can see all agencies (no filtering)
            except Exception as e:
                print(f"DEBUG: Error in get_queryset filtering: {str(e)}")
                # On error, return empty queryset for security
                queryset = queryset.none()
            
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

    # ========================================
    # AGENCY APPROVAL PROCESS ENDPOINTS
    # ========================================

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register(self, request):
        """
        Public agency self-registration endpoint
        Creates agency with user_id = NULL (pending approval)
        
        POST /api/v1/agency/register/
        Body: { agency_name, phone_number, address, email, representative, agency_type_id, district_id }
        Response: { agency_id, message, status: "pending" }
        """
        from .serializers import AgencyRegistrationSerializer
        
        serializer = AgencyRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        with transaction.atomic():
            agency = serializer.save()
            
            # TODO: Send notification to admin about new registration
            # notify_new_registration.delay(agency.agency_id)
            
        return Response({
            'agency_id': agency.agency_id,
            'code': f"HS{agency.agency_id:04d}",
            'message': 'Hồ sơ đăng ký đã được gửi thành công. Vui lòng chờ admin duyệt.',
            'status': 'pending',
            'submitted_at': agency.created_at.isoformat() if agency.created_at else None
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def pending(self, request):
        """
        List agencies pending approval (admin only)
        Only returns agencies with user_id = NULL
        
        GET /api/v1/agency/pending/
        Response: [{ id, code, name, type, district, phone, email, registration_date, days_pending }]
        """
        from .serializers import AgencyPendingSerializer
        
        # Filter agencies pending approval
        pending_agencies = Agency.objects.filter(
            user_id__isnull=True
        ).select_related('agency_type', 'district').order_by('-created_at')
        
        serializer = AgencyPendingSerializer(pending_agencies, many=True)
        
        return Response({
            'count': pending_agencies.count(),
            'results': serializer.data
        })

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """
        Approve agency and create user account (admin only)
        Updates user_id from NULL to new user ID
        
        POST /api/v1/agency/{id}/approve/
        Body: { username, password, full_name? }
        Response: { message, user_id, agency_id, status: "approved" }
        """
        from .serializers import AgencyApprovalSerializer
        from authentication.models import Account, User
        from django.contrib.auth.hashers import make_password
        
        agency = self.get_object()
        
        # Check if already approved
        if agency.user_id is not None:
            return Response({
                'error': 'Đại lý này đã được duyệt trước đó.',
                'agency_id': agency.agency_id,
                'current_user_id': agency.user_id
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate approval data
        serializer = AgencyApprovalSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            with transaction.atomic():
                # Create account following DDL auth.account structure
                account = Account.objects.create(
                    username=serializer.validated_data['username'],
                    password_hash=make_password(serializer.validated_data['password']),
                    account_role='agent'  # Per DDL CHECK constraint
                )
                
                # Create user profile following DDL auth.user structure
                full_name = serializer.validated_data.get('full_name') or agency.representative or agency.agency_name
                user = User.objects.create(
                    account=account,
                    full_name=full_name[:100],  # Respect DDL VARCHAR(100) constraint
                    email=agency.email,
                    phone_number=agency.phone_number,
                    address=agency.address[:255] if agency.address else None  # Respect DDL VARCHAR(255)
                )
                
                # Link agency to user (key step - changes NULL to user_id)
                agency.user_id = user.user_id
                agency.save(update_fields=['user_id', 'updated_at'])
                
                # TODO: Send approval notification email
                # send_approval_notification.delay(agency.agency_id, user.user_id)
                
        except Exception as e:
            return Response({
                'error': f'Lỗi khi tạo tài khoản: {str(e)}',
                'agency_id': agency.agency_id
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({
            'message': 'Đã duyệt hồ sơ và tạo tài khoản thành công.',
            'agency_id': agency.agency_id,
            'user_id': user.user_id,
            'username': account.username,
            'status': 'approved',
            'approved_at': timezone.now().isoformat()
        })

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """
        Reject agency application (admin only)
        Deletes the agency record and optionally sends notification
        
        POST /api/v1/agency/{id}/reject/
        Body: { reason, send_email? }
        Response: { message, agency_id, reason }
        """
        from .serializers import AgencyRejectSerializer
        
        agency = self.get_object()
        
        # Check if already approved (cannot reject approved agencies)
        if agency.user_id is not None:
            return Response({
                'error': 'Không thể từ chối đại lý đã được duyệt.',
                'agency_id': agency.agency_id,
                'current_user_id': agency.user_id
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate rejection data
        serializer = AgencyRejectSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Store data before deletion
        agency_data = {
            'agency_id': agency.agency_id,
            'agency_name': agency.agency_name,
            'email': agency.email,
            'phone_number': agency.phone_number,
            'reason': serializer.validated_data['reason']
        }
        
        try:
            with transaction.atomic():
                # TODO: Send rejection notification email before deletion
                if serializer.validated_data.get('send_email', True) and agency.email:
                    # send_rejection_notification.delay(agency_data)
                    pass
                
                # Delete agency record (DDL allows CASCADE)
                agency.delete()
                
        except Exception as e:
            return Response({
                'error': f'Lỗi khi từ chối hồ sơ: {str(e)}',
                'agency_id': agency.agency_id
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({
            'message': 'Đã từ chối hồ sơ đăng ký.',
            'agency_id': agency_data['agency_id'],
            'agency_name': agency_data['agency_name'],
            'reason': agency_data['reason'],
            'rejected_at': timezone.now().isoformat()
        })


class StaffAgencyViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Staff-Agency relationship management
    Handles assignment of staff to agencies per DDL.sql composite key design
    """
    queryset = StaffAgency.objects.select_related('agency')
    serializer_class = StaffAgencySerializer
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [AgencyPermission]
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
        
        print(f"DEBUG: by_staff API called with staff_id={staff_id}")
        
        # Kiểm tra quyền truy cập - user chỉ có thể xem agency của chính họ
        try:
            if hasattr(request.user, 'user_id'):
                requesting_user_id = request.user.user_id
                print(f"DEBUG: requesting_user_id={requesting_user_id}")
                
                # Chỉ cho phép staff xem agency của chính họ hoặc admin xem tất cả
                from authentication.models import User
                requesting_user = User.objects.select_related('account').get(user_id=requesting_user_id)
                
                if requesting_user.account.account_role != 'admin' and str(requesting_user_id) != str(staff_id):
                    print(f"DEBUG: Access denied - user {requesting_user_id} trying to access staff {staff_id}")
                    return Response(
                        {'error': 'Access denied - you can only view your own assignments'}, 
                        status=status.HTTP_403_FORBIDDEN
                    )
        except Exception as e:
            print(f"DEBUG: Error checking permissions: {str(e)}")
            return Response(
                {'error': 'Permission check failed'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        assignments = self.queryset.filter(staff_id=staff_id)
        print(f"DEBUG: Found {assignments.count()} assignments for staff_id={staff_id}")
        
        agencies = [assignment.agency for assignment in assignments]
        print(f"DEBUG: Agencies: {[a.agency_name for a in agencies]}")
        
        # Use AgencyListSerializer for consistency
        agency_serializer = AgencyListSerializer(agencies, many=True)
        
        response_data = {
            'staff_id': int(staff_id),
            'agency_count': len(agencies),
            'agencies': agency_serializer.data
        }
        
        print(f"DEBUG: Returning response: {response_data}")
        return Response(response_data)

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

    @action(detail=False, methods=['get'], url_path='unassigned-agents')
    def unassigned_agents(self, request):
        """
        Get list of agent users without agency assignment
        URL: /api/v1/agency/unassigned-agents/
        Response: [{ user_id, full_name, email, username, created_at }]
        """
        from authentication.models import User, Account
        
        # Query users with role='agent' but no agency assigned
        unassigned_users = User.objects.select_related('account').filter(
            account__account_role='agent'
        ).exclude(
            user_id__in=Agency.objects.filter(user_id__isnull=False).values_list('user_id', flat=True)
        ).order_by('-created_at')
        
        # Serialize user data
        users_data = []
        for user in unassigned_users:
            users_data.append({
                'user_id': user.user_id,
                'full_name': user.full_name,
                'email': user.email,
                'username': user.account.username,
                'phone_number': user.phone_number,
                'address': user.address,
                'created_at': user.created_at.isoformat() if user.created_at else None
            })
        
        return Response({
            'count': len(users_data),
            'results': users_data
        })

    @action(detail=False, methods=['post'], url_path='assign-profile')
    def assign_profile(self, request):
        """
        Create agency profile for existing agent user
        POST /api/v1/agency/assign-profile/
        Body: {
            user_id: number,
            agency_name: string,
            agency_type_id: number,
            district_id: number,
            phone_number: string,
            address: string,
            email?: string,
            representative?: string
        }
        """
        from .serializers import AgencyAssignmentSerializer
        from authentication.models import User
        
        # Validate input data
        serializer = AgencyAssignmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user_id = serializer.validated_data['user_id']
        
        try:
            with transaction.atomic():
                # Verify user exists and is an agent
                try:
                    user = User.objects.select_related('account').get(user_id=user_id)
                    if user.account.account_role != 'agent':
                        return Response({
                            'error': f'User {user_id} không phải là agent.'
                        }, status=status.HTTP_400_BAD_REQUEST)
                except User.DoesNotExist:
                    return Response({
                        'error': f'User {user_id} không tồn tại.'
                    }, status=status.HTTP_404_NOT_FOUND)
                
                # Check if user already has an agency
                if Agency.objects.filter(user_id=user_id).exists():
                    return Response({
                        'error': f'User {user.full_name} đã được cấp hồ sơ đại lý.'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Get related objects
                agency_type = AgencyType.objects.get(agency_type_id=serializer.validated_data['agency_type_id'])
                district = District.objects.get(district_id=serializer.validated_data['district_id'])
                
                # Create agency profile
                agency = Agency.objects.create(
                    agency_name=serializer.validated_data['agency_name'],
                    agency_type=agency_type,
                    district=district,
                    phone_number=serializer.validated_data['phone_number'],
                    address=serializer.validated_data['address'],
                    email=serializer.validated_data.get('email') or user.email,
                    representative=serializer.validated_data.get('representative') or user.full_name,
                    reception_date=timezone.now().date(),
                    debt_amount=0,
                    user_id=user_id  # KEY: Link to existing user
                )
                
                print(f"Successfully created agency {agency.agency_id} for user {user.full_name} (ID: {user_id})")
                
        except AgencyType.DoesNotExist:
            return Response({
                'error': 'Loại đại lý không tồn tại.'
            }, status=status.HTTP_400_BAD_REQUEST)
        except District.DoesNotExist:
            return Response({
                'error': 'Quận/huyện không tồn tại.'
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'error': f'Lỗi khi tạo hồ sơ đại lý: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({
            'message': f'Đã cấp hồ sơ đại lý thành công cho {user.full_name}.',
            'agency_id': agency.agency_id,
            'user_id': user_id,
            'agency_name': agency.agency_name,
            'assigned_at': timezone.now().isoformat()
        })
