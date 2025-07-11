from django.db import transaction
from django.utils import timezone
from decimal import Decimal
from authentication.exceptions import BusinessRuleViolation
from agency.models import Agency
from .models import Payment


class FinanceService:
    """
    Business logic service for finance operations
    Implements payment processing and debt management per docs/flow.md
    """
    
    @staticmethod
    @transaction.atomic
    def create_payment(payment_data, user):
        """
        Create payment and update agency debt
        Per docs/flow.md: Payment → Update debt - 
        """
        agency_id = payment_data['agency_id']
        amount_collected = Decimal(payment_data['amount_collected'])
        
        # Get agency
        try:
            agency = Agency.objects.get(agency_id=agency_id)
        except Agency.DoesNotExist:
            raise ValueError(f"Agency {agency_id} not found")
        
        # Validate payment amount
        if amount_collected <= 0:
            raise BusinessRuleViolation(
                code="INVALID_AMOUNT",
                message="Payment amount must be positive",
                details={"amount": float(amount_collected)}
            )
        
        # Check if payment exceeds debt (allow overpayment = credit)
        current_debt = agency.debt_amount
        remaining_debt = current_debt - amount_collected
        
        # FIX: The user_id field on the Payment model expects an integer, not an object.
        # This was the root cause of the "Must be 'Account' instance" error.
        user_id_to_save = user.user_id

        payment = Payment.objects.create(
            agency_id=agency_id,
            user_id=user_id_to_save,
            payment_date=payment_data.get('payment_date', timezone.now().date()),
            amount_collected=amount_collected
        )
        # Không cập nhật agency.debt_amount ở đây! Chỉ cập nhật khi PATCH sang completed.
        # agency.debt_amount = remaining_debt
        # agency.save()
        return payment, {
            'previous_debt': current_debt,
            'payment_amount': amount_collected,
            'new_debt_balance': remaining_debt,
            'is_credit': remaining_debt < 0,
            'credit_amount': abs(remaining_debt) if remaining_debt < 0 else 0
        }
    
    @staticmethod
    def get_debt_summary(agency_id=None):
        """Get debt summary for agencies"""
        from django.db.models import Sum, Max
        from inventory.models import Issue
        
        agencies_query = Agency.objects.select_related('agency_type')
        if agency_id:
            agencies_query = agencies_query.filter(agency_id=agency_id)
        
        summary = []
        
        for agency in agencies_query:
            # Get debt statistics
            total_issues = Issue.objects.filter(agency_id=agency.agency_id).aggregate(
                total=Sum('total_amount')
            )['total'] or Decimal('0.00')
            
            total_payments = Payment.objects.filter(agency_id=agency.agency_id).aggregate(
                total=Sum('amount_collected')
            )['total'] or Decimal('0.00')
            
            # Get last transaction dates
            last_payment = Payment.objects.filter(
                agency_id=agency.agency_id
            ).order_by('-payment_date').first()
            
            last_issue = Issue.objects.filter(
                agency_id=agency.agency_id
            ).order_by('-issue_date').first()
            
            # Calculate debt metrics
            debt_utilization = (agency.debt_amount / agency.agency_type.max_debt * 100) if agency.agency_type.max_debt > 0 else 0
            available_credit = agency.agency_type.max_debt - agency.debt_amount
            
            summary.append({
                'agency_id': agency.agency_id,
                'agency_name': agency.agency_name,
                'agency_type': agency.agency_type.type_name,
                'current_debt': float(agency.debt_amount),
                'debt_limit': float(agency.agency_type.max_debt),
                'debt_utilization_percent': float(debt_utilization),
                'available_credit': float(available_credit),
                'is_over_limit': agency.debt_amount > agency.agency_type.max_debt,
                'is_credit_balance': agency.debt_amount < 0,
                'total_lifetime_issues': float(total_issues),
                'total_lifetime_payments': float(total_payments),
                'last_payment_date': last_payment.payment_date if last_payment else None,
                'last_issue_date': last_issue.issue_date if last_issue else None
            })
        
        return summary
    
    @staticmethod
    def get_debt_aging_analysis(agency_id=None):
        """
        Get debt aging analysis
        Simplified version - in real system would analyze invoice aging
        """
        from datetime import date, timedelta
        from django.db.models import Q
        
        agencies_query = Agency.objects.select_related('agency_type').filter(debt_amount__gt=0)
        if agency_id:
            agencies_query = agencies_query.filter(agency_id=agency_id)
        
        aging_data = []
        today = date.today()
        
        for agency in agencies_query:
            # Get last payment date to estimate aging
            last_payment = Payment.objects.filter(
                agency_id=agency.agency_id
            ).order_by('-payment_date').first()
            
            # Estimate aging based on last payment
            if last_payment:
                days_since_payment = (today - last_payment.payment_date).days
            else:
                # If no payments, use reception date
                days_since_payment = (today - agency.reception_date).days if hasattr(agency, 'reception_date') else 0
            
            # Categorize aging
            aging_category = "90+ days"
            if days_since_payment <= 30:
                aging_category = "0-30 days"
            elif days_since_payment <= 60:
                aging_category = "31-60 days"
            elif days_since_payment <= 90:
                aging_category = "61-90 days"
            
            aging_data.append({
                'agency_id': agency.agency_id,
                'agency_name': agency.agency_name,
                'debt_amount': float(agency.debt_amount),
                'days_since_payment': days_since_payment,
                'aging_category': aging_category,
                'last_payment_date': last_payment.payment_date if last_payment else None
            })
        
        return aging_data
    
    @staticmethod
    def get_payment_history(agency_id, start_date=None, end_date=None):
        """Get detailed payment history for an agency"""
        payments_query = Payment.objects.filter(agency_id=agency_id)
        
        if start_date:
            payments_query = payments_query.filter(payment_date__gte=start_date)
        if end_date:
            payments_query = payments_query.filter(payment_date__lte=end_date)
        
        return payments_query.order_by('-payment_date')
    
    @staticmethod
    def calculate_monthly_revenue(start_date=None, end_date=None):
        """Calculate monthly revenue from issues"""
        from django.db.models import Sum
        from inventory.models import Issue
        
        issues_query = Issue.objects.all()
        
        if start_date:
            issues_query = issues_query.filter(issue_date__gte=start_date)
        if end_date:
            issues_query = issues_query.filter(issue_date__lte=end_date)
        
        # Group by month
        from django.db.models.functions import TruncMonth
        
        monthly_revenue = issues_query.annotate(
            month=TruncMonth('issue_date')
        ).values('month').annotate(
            total_revenue=Sum('total_amount')
        ).order_by('-month')
        
        return [
            {
                'month': item['month'].strftime('%Y-%m'),
                'revenue': float(item['total_revenue'])
            }
            for item in monthly_revenue
        ]


class DebtValidationService:
    """Service for debt-related validations and calculations"""
    
    @staticmethod
    def can_issue_to_agency(agency_id, additional_amount):
        """Check if agency can take on additional debt"""
        try:
            agency = Agency.objects.select_related('agency_type').get(agency_id=agency_id)
        except Agency.DoesNotExist:
            return False, "Agency not found"
        
        current_debt = agency.debt_amount
        max_debt = agency.agency_type.max_debt
        new_debt = current_debt + Decimal(additional_amount)
        
        if new_debt > max_debt:
            return False, {
                'current_debt': float(current_debt),
                'max_debt': float(max_debt),
                'additional_amount': float(additional_amount),
                'available_credit': float(max_debt - current_debt)
            }
        
        return True, {
            'available_credit': float(max_debt - new_debt)
        }
    
    @staticmethod
    def get_agencies_near_limit(threshold_percent=90):
        """Get agencies approaching their debt limit"""
        agencies = Agency.objects.select_related('agency_type').all()
        near_limit = []
        
        for agency in agencies:
            if agency.agency_type.max_debt > 0:
                utilization = (agency.debt_amount / agency.agency_type.max_debt) * 100
                
                if utilization >= threshold_percent:
                    near_limit.append({
                        'agency_id': agency.agency_id,
                        'agency_name': agency.agency_name,
                        'current_debt': float(agency.debt_amount),
                        'debt_limit': float(agency.agency_type.max_debt),
                        'utilization_percent': float(utilization)
                    })
        
        return sorted(near_limit, key=lambda x: x['utilization_percent'], reverse=True)