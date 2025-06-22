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


class PaymentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['agency_id', 'amount_collected', 'payment_date']
        
    def validate_agency_id(self, value):
        try:
            agency = Agency.objects.get(agency_id=value)
            return value
        except Agency.DoesNotExist:
            raise serializers.ValidationError("Agency does not exist")
            
    def validate_amount_collected(self, value):
        if value <= 0:
            raise serializers.ValidationError("Payment amount must be greater than 0")
        return value
        
    def validate(self, data):
        # Check if payment amount doesn't exceed debt
        try:
            agency = Agency.objects.get(agency_id=data['agency_id'])
            if data['amount_collected'] > agency.debt_amount:
                raise serializers.ValidationError({
                    'amount_collected': f"Payment amount ({data['amount_collected']}) cannot exceed agency debt ({agency.debt_amount})"
                })
        except Agency.DoesNotExist:
            pass  # Will be caught by agency_id validation
            
        return data
        
    def create(self, validated_data):
        user = self.context['request'].user
        
        # Create payment
        payment = Payment.objects.create(
            **validated_data,
            user_id=user.user_id
        )
        
        # Update agency debt
        agency = Agency.objects.get(agency_id=payment.agency_id)
        agency.debt_amount -= payment.amount_collected
        agency.save()
        
        return payment


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
        user = self.context['request'].user
        
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