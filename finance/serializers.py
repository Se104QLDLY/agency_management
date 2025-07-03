from rest_framework import serializers
from .models import Payment, Report
from agency.models import Agency
from authentication.models import User


class PaymentListSerializer(serializers.ModelSerializer):
    agency_name = serializers.SerializerMethodField()
    user_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Payment
        fields = [
            'payment_id', 'payment_date', 'agency_id', 'agency_name',
            'user_id', 'user_name', 'amount_collected', 'created_at'
        ]
        
    def get_agency_name(self, obj):
        try:
            agency = Agency.objects.get(agency_id=obj.agency_id)
            return agency.agency_name
        except Agency.DoesNotExist:
            return "Unknown Agency"
            
    def get_user_name(self, obj):
        try:
            user = User.objects.get(user_id=obj.user_id)
            return user.full_name
        except User.DoesNotExist:
            return "Unknown User"


class PaymentDetailSerializer(serializers.ModelSerializer):
    agency_name = serializers.SerializerMethodField()
    user_name = serializers.SerializerMethodField()
    debt_before = serializers.SerializerMethodField()
    debt_after = serializers.SerializerMethodField()
    
    class Meta:
        model = Payment
        fields = [
            'payment_id', 'payment_date', 'agency_id', 'agency_name',
            'user_id', 'user_name', 'amount_collected', 'created_at',
            'debt_before', 'debt_after'
        ]
        
    def get_agency_name(self, obj):
        try:
            agency = Agency.objects.get(agency_id=obj.agency_id)
            return agency.agency_name
        except Agency.DoesNotExist:
            return "Unknown Agency"
            
    def get_user_name(self, obj):
        try:
            user = User.objects.get(user_id=obj.user_id)
            return user.full_name
        except User.DoesNotExist:
            return "Unknown User"
            
    def get_debt_before(self, obj):
        try:
            agency = Agency.objects.get(agency_id=obj.agency_id)
            return agency.debt_amount + obj.amount_collected
        except Agency.DoesNotExist:
            return None
            
    def get_debt_after(self, obj):
        try:
            agency = Agency.objects.get(agency_id=obj.agency_id)
            return agency.debt_amount
        except Agency.DoesNotExist:
            return None


class PaymentCreateSerializer(serializers.Serializer):
    """
    A serializer for creating Payment: expects agency_id, amount_collected, payment_date.
    Validates business rules (positive amount, not exceeding debt) against agency.
    """
    agency_id = serializers.IntegerField()
    amount_collected = serializers.DecimalField(max_digits=15, decimal_places=2)
    payment_date = serializers.DateField()

    def validate_agency_id(self, value):
        """Checks if an agency with the given ID exists."""
        if not Agency.objects.filter(agency_id=value).exists():
            raise serializers.ValidationError(f"Đại lý với id '{value}' không tồn tại.")
        return value

    def validate(self, data):
        """
        Validates business rules against agency and amount.
        """
        agency = Agency.objects.get(agency_id=data.get('agency_id'))
        amount = data.get('amount_collected')

        # Business Rule: Collected amount must be positive
        if amount <= 0:
            raise serializers.ValidationError("Số tiền thu phải là một số dương.")

        # Business Rule: Collected amount cannot exceed current debt
        if amount > agency.debt_amount:
            raise serializers.ValidationError(
                f"Số tiền thu ({amount}) không được vượt quá công nợ hiện tại của đại lý ({agency.debt_amount})."
            )

        return data


class ReportListSerializer(serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Report
        fields = [
            'report_id', 'report_type', 'report_date',
            'created_by', 'created_by_name', 'created_at'
        ]
        
    def get_created_by_name(self, obj):
        try:
            user = User.objects.get(user_id=obj.created_by)
            return user.full_name
        except User.DoesNotExist:
            return "Unknown User"


class ReportDetailSerializer(serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Report
        fields = [
            'report_id', 'report_type', 'report_date', 'data',
            'created_by', 'created_by_name', 'created_at'
        ]
        
    def get_created_by_name(self, obj):
        try:
            user = User.objects.get(user_id=obj.created_by)
            return user.full_name
        except User.DoesNotExist:
            return "Unknown User"


class ReportCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ['report_type', 'report_date', 'data']
        
    def create(self, validated_data):
        # request.user is an Account object. We need the related User's ID.
        account = self.context['request'].user
        user = account.users.first()  # Get the first user associated with this account
        if not user:
            raise serializers.ValidationError("No user profile found for this account")
        
        report = Report.objects.create(
            **validated_data,
            created_by=user.user_id
        )
        
        return report


class DebtTransactionSerializer(serializers.Serializer):
    """Serializer for debt transaction data"""
    agency_id = serializers.IntegerField()
    agency_name = serializers.CharField(max_length=255)
    transaction_type = serializers.CharField(max_length=20)  # ISSUE or PAYMENT
    amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    transaction_date = serializers.DateField()
    reference_id = serializers.IntegerField()  # issue_id or payment_id
    running_balance = serializers.DecimalField(max_digits=15, decimal_places=2)


class DebtSummarySerializer(serializers.Serializer):
    """Serializer for debt summary data"""
    agency_id = serializers.IntegerField()
    agency_name = serializers.CharField(max_length=255)
    current_debt = serializers.DecimalField(max_digits=15, decimal_places=2)
    debt_limit = serializers.DecimalField(max_digits=15, decimal_places=2)
    debt_percentage = serializers.FloatField()
    last_payment_date = serializers.DateField(allow_null=True)
    last_issue_date = serializers.DateField(allow_null=True) 