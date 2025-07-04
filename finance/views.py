from django.shortcuts import render
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Sum, Max
from django.db import connection
from .models import Payment, Report
from .serializers import (
    PaymentListSerializer, PaymentDetailSerializer, PaymentCreateSerializer, PaymentStatusUpdateSerializer,
    ReportListSerializer, ReportDetailSerializer, ReportCreateSerializer,
    DebtTransactionSerializer, DebtSummarySerializer
)
from agency.models import Agency
from inventory.models import Issue
from authentication.permissions import CookieJWTAuthentication, FinancePermission
from .services import FinanceService
from authentication.models import User
from django.utils import timezone


class PaymentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing payments
    GET /api/v1/finance/payments/ - List payments with filters
    POST /api/v1/finance/payments/ - Create new payment
    GET /api/v1/finance/payments/{id}/ - Payment detail
    """
    queryset = Payment.objects.all()
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = []  # Temporarily remove for testing
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['agency_id', 'user_id', 'payment_date']
    ordering_fields = ['payment_date', 'amount_collected', 'created_at']
    ordering = ['-payment_date']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return PaymentListSerializer
        elif self.action == 'create':
            return PaymentCreateSerializer
        elif self.action == 'update_status':
            return PaymentStatusUpdateSerializer
        else:
            return PaymentDetailSerializer
    
    def get_queryset(self):
        queryset = Payment.objects.all()
        
        # Date range filtering
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        
        if date_from:
            queryset = queryset.filter(payment_date__gte=date_from)
        if date_to:
            queryset = queryset.filter(payment_date__lte=date_to)
            
        return queryset
    
    def create(self, request, *args, **kwargs):
        """
        Create payment with all logic self-contained in the view to ensure correctness.
        This bypasses the service layer to eliminate potential stale code issues.
        """
        from django.db import transaction
        from decimal import Decimal
        
        # Step 1: Validate incoming data using the serializer
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        validated_data = serializer.validated_data
        
        try:
            # Step 2: Begin a database transaction
            with transaction.atomic():
                # Step 3: Get all necessary objects
                agency_id = validated_data['agency_id']
                agency = Agency.objects.get(pk=agency_id)
                user_profile = request.user
                amount_collected = Decimal(validated_data['amount_collected'])

                # Step 4: Create the Payment object
                payment = Payment.objects.create(
                    agency_id=agency.agency_id,
                    user_id=user_profile.user_id,
                    payment_date=validated_data.get('payment_date'),
                    amount_collected=amount_collected
                )
                
                # Step 5: Update agency debt
                agency.debt_amount -= amount_collected
                agency.save()

                # Step 6: Return a success response
                response_serializer = PaymentDetailSerializer(payment)
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        except Agency.DoesNotExist:
            return Response({"error": "Agency not found."}, status=status.HTTP_404_NOT_FOUND)
        except User.DoesNotExist:
            return Response({"error": "User profile not found for authenticated account."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            # Catch any other unexpected errors
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['patch'], url_path='status', url_name='update-status')
    def update_status(self, request, pk=None):
        """Update the status of a payment."""
        payment = self.get_object()
        serializer = self.get_serializer(payment, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class ReportViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing reports
    GET /api/v1/finance/reports/ - List reports
    POST /api/v1/finance/reports/ - Create new report
    GET /api/v1/finance/reports/{id}/ - Report detail
    """
    queryset = Report.objects.all()
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = []  # Temporarily remove for testing
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['report_type', 'created_by']
    ordering_fields = ['report_date', 'created_at']
    ordering = ['-report_date']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ReportListSerializer
        elif self.action == 'create':
            return ReportCreateSerializer
        else:
            return ReportDetailSerializer

    def create(self, request, *args, **kwargs):
        """Create a new report, injecting the user from the request context."""
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class DebtViewSet(viewsets.ViewSet):
    """
    ViewSet for debt-related operations
    GET /api/v1/finance/debts/ - All debt transactions
    GET /api/v1/finance/debts/summary/ - Debt summary by agency
    GET /api/v1/finance/debts/aging/ - Debt aging analysis
    """
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = []  # Temporarily remove for testing
    
    def list(self, request):
        """Get all debt transactions with filters"""
        agency_id = request.query_params.get('agency_id')
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        
        # Build debt transaction data from issues and payments
        transactions = []
        
        # Get issues (debt increases)
        issues_query = Issue.objects.all()
        if agency_id:
            issues_query = issues_query.filter(agency_id=agency_id)
        if date_from:
            issues_query = issues_query.filter(issue_date__gte=date_from)
        if date_to:
            issues_query = issues_query.filter(issue_date__lte=date_to)
            
        for issue in issues_query:
            try:
                agency = Agency.objects.get(agency_id=issue.agency_id)
                transactions.append({
                    'agency_id': issue.agency_id,
                    'agency_name': agency.agency_name,
                    'transaction_type': 'ISSUE',
                    'amount': issue.total_amount,
                    'transaction_date': issue.issue_date,
                    'reference_id': issue.issue_id,
                    'running_balance': agency.debt_amount  # Current balance
                })
            except Agency.DoesNotExist:
                continue
        
        # Get payments (debt decreases)
        payments_query = Payment.objects.all()
        if agency_id:
            payments_query = payments_query.filter(agency_id=agency_id)
        if date_from:
            payments_query = payments_query.filter(payment_date__gte=date_from)
        if date_to:
            payments_query = payments_query.filter(payment_date__lte=date_to)
            
        for payment in payments_query:
            try:
                agency = Agency.objects.get(agency_id=payment.agency_id)
                transactions.append({
                    'agency_id': payment.agency_id,
                    'agency_name': agency.agency_name,
                    'transaction_type': 'PAYMENT',
                    'amount': payment.amount_collected,
                    'transaction_date': payment.payment_date,
                    'reference_id': payment.payment_id,
                    'running_balance': agency.debt_amount  # Current balance
                })
            except Agency.DoesNotExist:
                continue
        
        # Sort by date
        transactions.sort(key=lambda x: x['transaction_date'], reverse=True)
        
        serializer = DebtTransactionSerializer(transactions, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get debt summary for all agencies"""
        agency_id = request.query_params.get('agency_id')
        
        agencies_query = Agency.objects.select_related('agency_type')
        if agency_id:
            agencies_query = agencies_query.filter(agency_id=agency_id)
        
        summary_data = []
        
        for agency in agencies_query:
            # Get last payment and issue dates
            last_payment = Payment.objects.filter(agency_id=agency.agency_id).order_by('-payment_date').first()
            last_issue = Issue.objects.filter(agency_id=agency.agency_id).order_by('-issue_date').first()
            
            debt_percentage = (agency.debt_amount / agency.agency_type.max_debt * 100) if agency.agency_type.max_debt > 0 else 0
            
            summary_data.append({
                'agency_id': agency.agency_id,
                'agency_name': agency.agency_name,
                'current_debt': agency.debt_amount,
                'debt_limit': agency.agency_type.max_debt,
                'debt_percentage': debt_percentage,
                'last_payment_date': last_payment.payment_date if last_payment else None,
                'last_issue_date': last_issue.issue_date if last_issue else None
            })
        
        serializer = DebtSummarySerializer(summary_data, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def sales(self, request):
        """
        Generate a sales report grouped by month.
        Filters: ?agency_id=, ?from=YYYY-MM-DD, ?to=YYYY-MM-DD
        """
        from django.db.models.functions import TruncMonth
        from django.db.models import Count, Sum
        from decimal import Decimal

        agency_id = request.query_params.get('agency_id')
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')

        issues_query = Issue.objects.all()

        if agency_id:
            issues_query = issues_query.filter(agency_id=agency_id)
        if date_from:
            issues_query = issues_query.filter(issue_date__gte=date_from)
        if date_to:
            issues_query = issues_query.filter(issue_date__lte=date_to)

        sales_data = (
            issues_query
            .annotate(month=TruncMonth('issue_date'))
            .values('month')
            .annotate(
                total_revenue=Sum('total_amount', default=Decimal('0.0')),
                total_issues=Count('issue_id'),
                new_debt_generated=Sum('total_amount', default=Decimal('0.0')) # Simplified, assumes all issues generate debt
            )
            .order_by('month')
        )

        # Format the month to string 'YYYY-MM'
        formatted_data = [
            {
                "month": item['month'].strftime('%Y-%m'),
                "total_revenue": item['total_revenue'],
                "total_issues": item['total_issues'],
                "new_debt_generated": item['new_debt_generated'],
            }
            for item in sales_data
        ]
        
        return Response(formatted_data)
    
    @action(detail=False, methods=['get'])
    def aging(self, request):
        """Get debt aging analysis"""
        agency_id = request.query_params.get('agency_id')
        
        # This is a simplified aging analysis
        # In a real system, you'd calculate based on invoice dates and aging buckets
        agencies_query = Agency.objects.select_related('agency_type').filter(debt_amount__gt=0)
        if agency_id:
            agencies_query = agencies_query.filter(agency_id=agency_id)
        
        aging_data = {
            'total_debt': 0,
            'agencies_count': 0,
            'aging_buckets': {
                '0-30': {'count': 0, 'amount': 0},
                '31-60': {'count': 0, 'amount': 0},
                '61-90': {'count': 0, 'amount': 0},
                '90+': {'count': 0, 'amount': 0}
            },
            'agencies': []
        }
        
        for agency in agencies_query:
            # Get last issue to estimate aging (simplified)
            last_issue = Issue.objects.filter(agency_id=agency.agency_id).order_by('-issue_date').first()
            
            if last_issue:
                days_since_issue = (timezone.now().date() - last_issue.issue_date).days
                
                bucket = '90+'
                if days_since_issue <= 30:
                    bucket = '0-30'
                elif days_since_issue <= 60:
                    bucket = '31-60'
                elif days_since_issue <= 90:
                    bucket = '61-90'
                
                aging_data['aging_buckets'][bucket]['count'] += 1
                aging_data['aging_buckets'][bucket]['amount'] += float(agency.debt_amount)
            
            aging_data['total_debt'] += float(agency.debt_amount)
            aging_data['agencies_count'] += 1
            
            aging_data['agencies'].append({
                'agency_id': agency.agency_id,
                'agency_name': agency.agency_name,
                'debt_amount': float(agency.debt_amount),
                'days_since_issue': days_since_issue if last_issue else None,
                'last_issue_date': last_issue.issue_date if last_issue else None
            })
            
        return Response(aging_data)
