from rest_framework import serializers
from .models import Unit, Item, Receipt, ReceiptDetail, Issue, IssueDetail


# Đơn vị tính
class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = ['id', 'name']


# Mặt hàng
class ItemSerializer(serializers.ModelSerializer):
    unit_name = serializers.CharField(source='unit.name', read_only=True)

    class Meta:
        model = Item
        fields = [
            'id', 'name', 'unit', 'unit_name',
            'price', 'stock_quantity', 'description'
        ]


# Phiếu nhập - chi tiết
class ReceiptDetailSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source='item.name', read_only=True)

    class Meta:
        model = ReceiptDetail
        fields = [
            'id', 'receipt', 'item', 'item_name',
            'quantity', 'unit_price', 'line_total'
        ]

    def validate(self, data):
        if data['quantity'] <= 0:
            raise serializers.ValidationError("Số lượng phải > 0")
        if data['unit_price'] < 0:
            raise serializers.ValidationError("Đơn giá không hợp lệ")
        return data


# Phiếu nhập
class ReceiptSerializer(serializers.ModelSerializer):
    agency_name = serializers.CharField(source='agency.name', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    details = ReceiptDetailSerializer(many=True, read_only=True, source='receiptdetail_set')

    class Meta:
        model = Receipt
        fields = [
            'id', 'receipt_date', 'agency', 'agency_name',
            'user', 'user_name', 'total_amount', 'created_at', 'details'
        ]

    def create(self, validated_data):
        # Tự động cập nhật tổng tiền nếu cần
        return super().create(validated_data)


# Phiếu xuất - chi tiết
class IssueDetailSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source='item.name', read_only=True)

    class Meta:
        model = IssueDetail
        fields = [
            'id', 'issue', 'item', 'item_name',
            'quantity', 'unit_price', 'line_total'
        ]

    def validate(self, data):
        if data['quantity'] <= 0:
            raise serializers.ValidationError("Số lượng phải > 0")
        if data['unit_price'] < 0:
            raise serializers.ValidationError("Đơn giá không hợp lệ")
        return data


# Phiếu xuất
class IssueSerializer(serializers.ModelSerializer):
    agency_name = serializers.CharField(source='agency.name', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    details = IssueDetailSerializer(many=True, read_only=True, source='issuedetail_set')

    class Meta:
        model = Issue
        fields = [
            'id', 'issue_date', 'agency', 'agency_name',
            'user', 'user_name', 'total_amount', 'created_at', 'details'
        ]

    def create(self, validated_data):
        # Có thể tính lại tổng tiền nếu cần
        return super().create(validated_data)
