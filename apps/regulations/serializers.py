from rest_framework import serializers
from .models import Regulation

class RegulationSerializer(serializers.ModelSerializer):
    last_updated_by_username = serializers.CharField(source='last_updated_by.username', read_only=True)

    class Meta:
        model = Regulation
        fields = [
            'regulation_key', 'regulation_value',
            'description', 'last_updated_by', 'last_updated_by_username', 'updated_at'
        ]
        read_only_fields = ['last_updated_by', 'updated_at']

    def create(self, validated_data):
        validated_data['last_updated_by'] = self.context['request'].user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data['last_updated_by'] = self.context['request'].user
        return super().update(instance, validated_data)
