
from rest_framework import serializers
from .models import Agency, AgencyType, District

class AgencyTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgencyType
        fields = '__all__'

class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = '__all__'

class AgencySerializer(serializers.ModelSerializer):
    agency_type = AgencyTypeSerializer(read_only=True)
    agency_type_id = serializers.PrimaryKeyRelatedField(
        queryset=AgencyType.objects.all(), source='agency_type', write_only=True
    )

    district = DistrictSerializer(read_only=True)
    district_id = serializers.PrimaryKeyRelatedField(
        queryset=District.objects.all(), source='district', write_only=True
    )

    class Meta:
        model = Agency
        fields = [
            'id', 'name',
            'agency_type', 'agency_type_id',
            'district', 'district_id',
            'address', 'phone', 'email',
            'representative', 'debt',
            'created_at', 'updated_at'
        ]

    def validate_email(self, value):
        if Agency.objects.exclude(pk=self.instance.pk if self.instance else None).filter(email=value).exists():
            raise serializers.ValidationError("Email này đã tồn tại.")
        return value

    def validate_phone(self, value):
        if Agency.objects.exclude(pk=self.instance.pk if self.instance else None).filter(phone=value).exists():
            raise serializers.ValidationError("Số điện thoại này đã tồn tại.")
        return value

