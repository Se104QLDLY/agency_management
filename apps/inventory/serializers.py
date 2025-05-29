from rest_framework import serializers
from .models import Unit, Item, Receipt, ReceiptDetail, Issue, IssueDetail

class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = '__all__'

class ItemSerializer(serializers.ModelSerializer):
    unit_name = serializers.CharField(source='unit.name', read_only=True)

    class Meta:
        model = Item
        fields = ['id', 'name', 'unit', 'unit_name', 'price', 'stock_quantity', 'description']

class ReceiptDetailSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source='item.name', read_only=True)

    class Meta:
        model = ReceiptDetail
        fields = ['id', 'receipt', 'item', 'item_name', 'quantity', 'unit_price', 'line_total']

class ReceiptSerializer(serializers.ModelSerializer):
    details = ReceiptDetailSerializer(many=True, read_only=True)
    total_amount = serializers.DecimalField(max_digits=18, decimal_places=2, read_only=True)

    class Meta:
        model = Receipt
        fields = ['id', 'user', 'created_at', 'total_amount', 'details']

class IssueDetailSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source='item.name', read_only=True)

    class Meta:
        model = IssueDetail
        fields = ['id', 'issue', 'item', 'item_name', 'quantity', 'unit_price', 'line_total']

class IssueSerializer(serializers.ModelSerializer):
    details = IssueDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Issue
        fields = ['id', 'user', 'agency', 'created_at', 'total_amount', 'details']
