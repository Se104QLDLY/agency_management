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
            'user_id', 'user_name', 'amount_collected', 'status', 'status_reason', 'created_at'
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
            'user_id', 'user_name', 'amount_collected', 'status', 'status_reason', 'created_at',
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


class PaymentStatusUpdateSerializer(serializers.ModelSerializer):
    status = serializers.CharField()  # Override to allow alias mapping and custom validation
    class Meta:
        model = Payment
        fields = ['status', 'status_reason']

    def validate_status(self, value):
        import logging
        logger = logging.getLogger(__name__)
        # Map aliases to match DDL status values
        alias_map = {
            'paid': 'completed',
            'done': 'completed',
            'success': 'completed',
            'confirmed': 'completed',  # Map từ confirmed sang completed để khớp DDL
            'canceled': 'failed',
            'cancel': 'failed',
            'cancelled': 'failed',
            'huy': 'failed',
        }
        if isinstance(value, str) and value.lower() in alias_map:
            logger.info(f"validate_status: auto-mapping alias '{value}' -> '{alias_map[value.lower()]}'")
            value = alias_map[value.lower()]
        allowed_statuses = [choice[0] for choice in Payment.STATUS_CHOICES]
        if value not in allowed_statuses:
            logger.warning(f"validate_status: {value} not in {allowed_statuses}")
            raise serializers.ValidationError(f"Status must be one of {allowed_statuses}")
        return value

    def validate(self, data):
        # Bắt buộc phải có trường status khi PATCH
        if 'status' not in data:
            raise serializers.ValidationError({'status': 'This field is required.'})
        return data

    def update(self, instance, validated_data):
        import logging
        import traceback
        logger = logging.getLogger(__name__)
        logger.debug(f"PATCH validated_data: {validated_data}")
        logger.debug(f"PATCH instance.status: {instance.status}")
        old_status = instance.status
        new_status = validated_data.get('status', old_status)
        logger.debug(f"PATCH old_status: {old_status}, new_status: {new_status}")

        # Allow PATCH to update status_reason even if already completed/failed, but block status change
        if old_status in ['completed', 'failed']:
            if new_status != old_status:
                logger.warning(f"[Payment PATCH] Cannot change status from {old_status} to {new_status}. Payment ID: {instance.payment_id}")
                # Return 409 Conflict for status change attempts after completed/failed
                raise serializers.ValidationError({
                    "error": f"Cannot change status from {old_status} to {new_status}.",
                    "current_status": old_status,
                    "payment_id": instance.payment_id,
                    "code": "CONFLICT"
                }, code='conflict')
            # Allow updating status_reason only
            instance.status_reason = validated_data.get('status_reason', instance.status_reason)
            instance.save()
            return instance

        # Debt calculation is now handled by database trigger when status changes to 'completed'
        # Only validate that payment doesn't exceed debt before allowing status change
        if old_status == 'pending' and new_status == 'completed':
            try:
                agency = Agency.objects.get(agency_id=instance.agency_id)
                if instance.amount_collected > agency.debt_amount:
                    logger.warning(f"[Payment PATCH] Số tiền thu ({instance.amount_collected}) vượt công nợ ({agency.debt_amount}) của agency {agency.agency_id}")
                    raise serializers.ValidationError({
                        "error": f"Số tiền thu ({instance.amount_collected}) không được vượt quá công nợ hiện tại của đại lý ({agency.debt_amount}).",
                        "current_status": old_status,
                        "payment_id": instance.payment_id,
                        "code": "AMOUNT_EXCEEDS_DEBT"
                    }, code='conflict')
                logger.info(f"[Payment PATCH] Validation passed for payment {instance.payment_id}, debt update will be handled by trigger")
            except Agency.DoesNotExist:
                logger.error(f"[Payment PATCH] Agency không tồn tại: {instance.agency_id}")
                raise serializers.ValidationError({
                    "error": "Agency does not exist.",
                    "payment_id": instance.payment_id,
                    "code": "AGENCY_NOT_FOUND"
                }, code='not_found')
            except Exception as e:
                logger.error(f"[Payment PATCH] Exception: {e}\n{traceback.format_exc()}")
                raise serializers.ValidationError({
                    "error": f"Lỗi hệ thống: {str(e)}",
                    "payment_id": instance.payment_id,
                    "code": "SERVER_ERROR"
                }, code='server_error')
        # Update status and status_reason
        instance.status = new_status
        instance.status_reason = validated_data.get('status_reason', instance.status_reason)
        instance.save()
        return instance


class ReportListSerializer(serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField()
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = Report
        fields = [
            'report_id', 'report_type', 'report_date',
            'created_by', 'created_by_name', 'created_at', 'created_by_username'
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