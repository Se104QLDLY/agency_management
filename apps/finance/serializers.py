from rest_framework import serializers
from .models import Payment

class PaymentSerializer(serializers.ModelSerializer):
    agency_name = serializers.CharField(source='agency.name', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id', 'payment_date', 'agency', 'agency_name',
            'user', 'user_name', 'amount_collected', 'created_at'
        ]

    def validate(self, data):
        agency = data.get('agency')
        amount = data.get('amount_collected')

        if agency and amount > agency.debt:
            raise serializers.ValidationError(
                f"Số tiền thu ({amount}) vượt quá công nợ hiện tại ({agency.debt})"
            )
        return data
