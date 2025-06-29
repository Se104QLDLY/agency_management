from rest_framework import serializers
from .models import Unit, Item, Receipt, ReceiptDetail, Issue, IssueDetail
from agency.models import Agency
from authentication.models import User


class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = ['unit_id', 'unit_name']


class ItemListSerializer(serializers.ModelSerializer):
    unit_name = serializers.CharField(source='unit.unit_name', read_only=True)
    
    class Meta:
        model = Item
        fields = [
            'item_id', 'item_name', 'unit', 'unit_name', 
            'price', 'stock_quantity', 'description', 'created_at', 'updated_at'
        ]


class ItemDetailSerializer(serializers.ModelSerializer):
    unit_name = serializers.CharField(source='unit.unit_name', read_only=True)
    
    class Meta:
        model = Item
        fields = [
            'item_id', 'item_name', 'unit', 'unit_name',
            'price', 'stock_quantity', 'description', 'created_at', 'updated_at'
        ]


class ItemCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['item_name', 'unit', 'price', 'stock_quantity', 'description']
        
    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than 0")
        return value


class ReceiptDetailSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source='item.item_name', read_only=True)
    
    class Meta:
        model = ReceiptDetail
        fields = [
            'receipt_detail_id', 'item', 'item_name', 
            'quantity', 'unit_price', 'line_total'
        ]


class ReceiptDetailCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReceiptDetail
        fields = ['item', 'quantity', 'unit_price']
        
    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than 0")
        return value
        
    def validate_unit_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Unit price must be greater than 0")
        return value


class ReceiptListSerializer(serializers.ModelSerializer):
    agency_name = serializers.SerializerMethodField()
    user_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Receipt
        fields = [
            'receipt_id', 'receipt_date', 'agency_id', 'agency_name',
            'user_id', 'user_name', 'total_amount', 'created_at'
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


class ReceiptDetailNestedSerializer(serializers.ModelSerializer):
    details = ReceiptDetailSerializer(many=True, read_only=True)
        
    class Meta:
        model = Receipt
        fields = [
            'receipt_id', 'receipt_date', 'agency_id', 'user_id',
            'total_amount', 'created_at', 'details'
        ]


class ReceiptCreateSerializer(serializers.ModelSerializer):
    items = ReceiptDetailCreateSerializer(many=True, write_only=True)
    
    class Meta:
        model = Receipt
        fields = ['agency_id', 'receipt_date', 'items']
        
    def validate_agency_id(self, value):
        if not Agency.objects.filter(agency_id=value).exists():
            raise serializers.ValidationError("Agency does not exist")
        return value
        
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        user = self.context['request'].user
        
        # Create receipt
        receipt = Receipt.objects.create(
            **validated_data,
            user_id=user.user_id,
            total_amount=0  # Will be calculated by trigger
        )
        
        # Create receipt details
        for item_data in items_data:
            line_total = item_data['quantity'] * item_data['unit_price']
            ReceiptDetail.objects.create(
                receipt=receipt,
                line_total=line_total,
                **item_data
            )
            
            # Update item stock
            item = item_data['item']
            item.stock_quantity += item_data['quantity']
            item.save()
        
        return receipt


class IssueDetailSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source='item.item_name', read_only=True)
    
    class Meta:
        model = IssueDetail
        fields = [
            'issue_detail_id', 'item', 'item_name',
            'quantity', 'unit_price', 'line_total'
        ]


class IssueDetailCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = IssueDetail
        fields = ['item', 'quantity']
        
    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than 0")
        return value


class IssueListSerializer(serializers.ModelSerializer):
    agency_name = serializers.SerializerMethodField()
    user_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Issue
        fields = [
            'issue_id', 'issue_date', 'agency_id', 'agency_name',
            'user_id', 'user_name', 'total_amount', 'status', 'status_reason', 'created_at'
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


class IssueDetailNestedSerializer(serializers.ModelSerializer):
    details = IssueDetailSerializer(many=True, read_only=True)
    debt_impact = serializers.SerializerMethodField()
    
    class Meta:
        model = Issue
        fields = [
            'issue_id', 'issue_date', 'agency_id', 'user_id',
            'total_amount', 'status', 'status_reason', 'created_at', 'details', 'debt_impact'
        ]
        
    def get_debt_impact(self, obj):
        try:
            agency = Agency.objects.get(agency_id=obj.agency_id)
            return {
                'previous_debt': agency.debt_amount - obj.total_amount,
                'issue_amount': obj.total_amount,
                'new_debt': agency.debt_amount
            }
        except Agency.DoesNotExist:
            return None


class IssueCreateSerializer(serializers.ModelSerializer):
    items = IssueDetailCreateSerializer(many=True, write_only=True)
    
    class Meta:
        model = Issue
        fields = ['agency_id', 'issue_date', 'items']
        
    def validate_agency_id(self, value):
        if not Agency.objects.filter(agency_id=value).exists():
            raise serializers.ValidationError("Agency does not exist")
        return value
        
    def validate(self, data):
        # Check stock availability and debt limit
        agency = Agency.objects.get(agency_id=data['agency_id'])
        total_amount = 0
        
        for item_data in data['items']:
            item = item_data['item']
            quantity = item_data['quantity']
            
            # Check stock
            if item.stock_quantity < quantity:
                raise serializers.ValidationError({
                    'items': f"Insufficient stock for {item.item_name}. Available: {item.stock_quantity}, Requested: {quantity}"
                })
                
            # Calculate total
            total_amount += quantity * item.price
            
        # Check debt limit
        agency_type = agency.agency_type
        if agency.debt_amount + total_amount > agency_type.max_debt:
            raise serializers.ValidationError({
                'debt_limit': {
                    'code': 'DEBT_LIMIT',
                    'message': 'Issue would exceed agency debt limit',
                    'max_debt': agency_type.max_debt,
                    'current_debt': agency.debt_amount,
                    'issue_amount': total_amount,
                    'would_be': agency.debt_amount + total_amount
                }
            })
            
        return data
        
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        user = self.context['request'].user
        
        # Handle case when no authentication (for testing)
        user_id = user.user_id if hasattr(user, 'user_id') else 1  # Default to admin user
        
        # Create issue
        issue = Issue.objects.create(
            **validated_data,
            user_id=user_id,
            total_amount=0  # Will be calculated
        )
        
        total_amount = 0
        
        # Create issue details
        for item_data in items_data:
            item = item_data['item']
            quantity = item_data['quantity']
            unit_price = item.price
            line_total = quantity * unit_price
            
            IssueDetail.objects.create(
                issue=issue,
                item=item,
                quantity=quantity,
                unit_price=unit_price,
                line_total=line_total
            )
            
            # Stock update handled by database trigger reduce_stock_on_issue
            # No need to update via Django ORM to avoid double update
            
            total_amount += line_total
        
        # Update issue total and agency debt
        issue.total_amount = total_amount
        issue.save()
        
        # Update agency debt
        agency = Agency.objects.get(agency_id=issue.agency_id)
        agency.debt_amount += total_amount
        agency.save()
        
        return issue 