from rest_framework import serializers
from .models import Regulation


class RegulationListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Regulation
        fields = ['regulation_key', 'regulation_value', 'description', 'updated_at']


class RegulationDetailSerializer(serializers.ModelSerializer):
    updated_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Regulation
        fields = [
            'regulation_key', 'regulation_value', 'description',
            'last_updated_by', 'updated_by_name', 'updated_at'
        ]
        
    def get_updated_by_name(self, obj):
        if obj.last_updated_by:
            try:
                from authentication.models import User
                user = User.objects.get(user_id=obj.last_updated_by)
                return user.full_name
            except User.DoesNotExist:
                return "Unknown User"
        return None


class RegulationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Regulation
        fields = ['regulation_key', 'regulation_value', 'description']
        
    def create(self, validated_data):
        user = self.context['request'].user
        
        # Create new regulation
        regulation = Regulation.objects.create(
            regulation_key=validated_data['regulation_key'],
            regulation_value=validated_data['regulation_value'],
            description=validated_data.get('description', ''),
            last_updated_by=user.user_id
        )
        
        return regulation


class RegulationUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Regulation
        fields = ['regulation_value', 'description']
        
    def update(self, instance, validated_data):
        user = self.context['request'].user
        
        # Update regulation
        instance.regulation_value = validated_data.get('regulation_value', instance.regulation_value)
        instance.description = validated_data.get('description', instance.description)
        instance.last_updated_by = user.user_id
        instance.save()
        
        return instance


class RegulationHistorySerializer(serializers.Serializer):
    """Serializer for regulation change history"""
    regulation_key = serializers.CharField(max_length=50)
    old_value = serializers.CharField(max_length=255, allow_null=True)
    new_value = serializers.CharField(max_length=255)
    changed_by = serializers.IntegerField()
    changed_by_name = serializers.CharField(max_length=100, allow_null=True)
    changed_at = serializers.DateTimeField() 