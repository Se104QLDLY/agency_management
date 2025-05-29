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
            'id', 'name', 'agency_type', 'agency_type_id',
            'district', 'district_id', 'address',
            'phone', 'email', 'representative',
            'reception_date', 'debt', 'created_at', 'updated_at'
        ]

    def validate_email(self, value):
        qs = Agency.objects.exclude(pk=self.instance.pk if self.instance else None)
        if qs.filter(email=value).exists():
            raise serializers.ValidationError("Email này đã tồn tại.")
        return value

    def validate_phone(self, value):
        qs = Agency.objects.exclude(pk=self.instance.pk if self.instance else None)
        if qs.filter(phone=value).exists():
            raise serializers.ValidationError("Số điện thoại này đã tồn tại.")
        return value

    def validate(self, data):
        agency_type = data.get('agency_type') or (self.instance.agency_type if self.instance else None)
        district = data.get('district') or (self.instance.district if self.instance else None)
        debt = data.get('debt', self.instance.debt if self.instance else 0)

        if agency_type and debt > agency_type.max_debt:
            raise serializers.ValidationError(
                f"Nợ hiện tại ({debt}) vượt quá hạn mức cho phép ({agency_type.max_debt})."
            )

        if district and not self.instance:
            if Agency.objects.filter(district=district).count() >= district.max_agencies:
                raise serializers.ValidationError(
                    f"Quận {district.name} đã đạt giới hạn đại lý tối đa ({district.max_agencies})."
                )

        return data
