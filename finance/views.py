from django.shortcuts import render
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Sum, Max
from django.db import connection
from django.utils import timezone
from datetime import datetime, date
from .models import Payment, Report
from .serializers import (
    PaymentListSerializer, PaymentDetailSerializer, PaymentCreateSerializer, PaymentStatusUpdateSerializer,
    ReportListSerializer, ReportDetailSerializer, ReportCreateSerializer,
    DebtTransactionSerializer, DebtSummarySerializer
)
from agency.models import Agency
from inventory.models import Issue, Item
from authentication.permissions import CookieJWTAuthentication, FinancePermission
from .services import FinanceService
from .export_utils import ReportExporter
from authentication.models import User


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
        from django.utils import timezone
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
                # Step 4: Create the Payment object (status defaults to 'pending')
                payment = Payment.objects.create(
                    agency_id=agency.agency_id,
                    user_id=user_profile.user_id,
                    payment_date=validated_data.get('payment_date'),
                    amount_collected=amount_collected,
                    created_at=timezone.now()
                )
                # Tuyệt đối không trừ công nợ ở đây!
                # Debt update is handled ONLY when payment status is set to 'completed' in the serializer
                # Step 6: Return a success response
                response_serializer = PaymentDetailSerializer(payment)
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        except Agency.DoesNotExist:
            return Response({"error": "Agency not found."}, status=status.HTTP_404_NOT_FOUND)
        except User.DoesNotExist:
            return Response({"error": "User profile not found for authenticated account."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            # Catch any other unexpected errors
            import traceback
            return Response({"error": str(e), "trace": traceback.format_exc()}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['patch'], url_path='status', url_name='update-status')
    def update_status(self, request, pk=None):
        """Update the status of a payment."""
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"PATCH /payments/{pk}/status/ request.data: {request.data}")
        payment = self.get_object()
        serializer = self.get_serializer(payment, data=request.data, partial=True)
        if not serializer.is_valid():
            logger.error(f"PATCH /payments/{pk}/status/ errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        logger.info(f"PATCH /payments/{pk}/status/ success: {serializer.data}")
        return Response(serializer.data)


class ReportViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing reports
    GET /api/v1/finance/reports/ - List reports
    POST /api/v1/finance/reports/ - Create new report
    GET /api/v1/finance/reports/{id}/ - Report detail
    GET /api/v1/finance/reports/generate/ - Generate report with filters
    GET /api/v1/finance/reports/{id}/export_excel/ - Export to Excel
    GET /api/v1/finance/reports/{id}/export_pdf/ - Export to PDF
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

    @action(detail=False, methods=['post'])
    def generate(self, request):
        """Generate report with filters"""
        report_type = request.data.get('report_type')
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        agency_id = request.data.get('agency_id')
        
        print(f"DEBUG: Generating report - type: {report_type}, start: {start_date}, end: {end_date}, agency: {agency_id}")
        
        if not report_type:
            return Response({'error': 'report_type is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Get user for created_by - request.user is already a User object
            user = request.user
            print(f"DEBUG: user = {user}, type = {type(user)}")
            
            if not hasattr(user, 'user_id'):
                print(f"DEBUG: user has no user_id attribute")
                return Response({'error': 'Invalid user object'}, status=status.HTTP_400_BAD_REQUEST)
            
            print(f"DEBUG: user.user_id = {user.user_id}")
            
            # Parse dates
            if start_date:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            if end_date:
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            
            print(f"DEBUG: Parsed dates - start: {start_date}, end: {end_date}")
            
            # Generate report based on type
            if report_type == 'sales':
                print(f"DEBUG: Generating sales report")
                report = self._generate_sales_report(date.today(), user.user_id, agency_id, start_date, end_date)
            elif report_type == 'debt':
                print(f"DEBUG: Generating debt report")
                report = self._generate_debt_report(start_date or date.today(), user.user_id, agency_id, start_date, end_date)
            elif report_type == 'inventory':
                print(f"DEBUG: Generating inventory report")
                report = self._generate_inventory_report(start_date or date.today(), user.user_id)
            else:
                return Response({'error': 'Invalid report_type'}, status=status.HTTP_400_BAD_REQUEST)
            
            print(f"DEBUG: Report generated successfully - ID: {report.report_id}")
            
            serializer = ReportDetailSerializer(report)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            print(f"DEBUG ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _generate_sales_report(self, for_date, created_by, agency_id=None, start_date=None, end_date=None):
        """Generate sales report from Issue data with status='delivered'"""
        # Get sales data from Issue table - use date range if provided, otherwise use for_date
        if start_date and end_date:
            sales_query = Issue.objects.filter(
                issue_date__gte=start_date,
                issue_date__lte=end_date,
                status='delivered'  # Chỉ tính phiếu đã giao hàng
            )
        else:
            # Fallback to original logic using for_date
            sales_query = Issue.objects.filter(
                issue_date__year=for_date.year,
                issue_date__month=for_date.month,
                status='delivered'  # Chỉ tính phiếu đã giao hàng
            )
        
        if agency_id:
            sales_query = sales_query.filter(agency_id=agency_id)
        
        # Get unique agency IDs and preload agencies
        agency_ids = set(sales_query.values_list('agency_id', flat=True))
        agencies = {agency.agency_id: agency.agency_name for agency in Agency.objects.filter(agency_id__in=agency_ids)}
        
        # Aggregate by agency
        agency_sales = {}
        for issue in sales_query:
            agency_id = issue.agency_id
            if agency_id not in agencies:
                continue  # Skip if agency doesn't exist
                
            if agency_id not in agency_sales:
                agency_sales[agency_id] = {
                    'agency_id': agency_id,
                    'agency_name': agencies[agency_id],
                    'total_sales': 0,
                    'total_issues': 0
                }
            agency_sales[agency_id]['total_sales'] += float(issue.total_amount)
            agency_sales[agency_id]['total_issues'] += 1
        
        # Create report
        return Report.objects.create(
            report_type='sales',
            report_date=for_date,
            data={'sales': list(agency_sales.values())},
            created_by=created_by
        )

    def _generate_debt_report(self, for_date, created_by, agency_id=None, start_date=None, end_date=None):
        """Generate debt report using improved logic"""
        return Report.objects.create_debt_report(for_date, created_by, agency_id, start_date, end_date)

    def _generate_inventory_report(self, for_date, created_by):
        """Generate inventory report"""
        return Report.objects.create_inventory_report(for_date, created_by)

    @action(detail=True, methods=['get'])
    def export_excel(self, request, pk=None):
        """Export report to Excel"""
        report = self.get_object()
        
        # Determine title based on report type
        titles = {
            'sales': 'Báo cáo doanh số',
            'debt': 'Báo cáo công nợ',
            'inventory': 'Báo cáo tồn kho'
        }
        title = titles.get(report.report_type, 'Báo cáo')
        
        exporter = ReportExporter(report.data, report.report_type, title)
        return exporter.export_to_excel()

    @action(detail=True, methods=['get'])
    def export_pdf(self, request, pk=None):
        """Export report to PDF"""
        report = self.get_object()
        
        # Determine title based on report type
        titles = {
            'sales': 'Báo cáo doanh số',
            'debt': 'Báo cáo công nợ',
            'inventory': 'Báo cáo tồn kho'
        }
        title = titles.get(report.report_type, 'Báo cáo')
        
        exporter = ReportExporter(report.data, report.report_type, title)
        return exporter.export_to_pdf()

    @action(detail=False, methods=['get'])
    def agencies(self, request):
        """Get list of agencies for dropdown selection"""
        agencies = Agency.objects.all().values('agency_id', 'agency_name')
        return Response(list(agencies))


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
