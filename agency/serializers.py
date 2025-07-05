from rest_framework import serializers
from .models import AgencyType, District, Agency, StaffAgency


class AgencyTypeSerializer(serializers.ModelSerializer):
    """Serializer for AgencyType model"""
    
    class Meta:
        model = AgencyType
        fields = ['agency_type_id', 'type_name', 'max_debt', 'description']
        read_only_fields = ['agency_type_id']


class DistrictSerializer(serializers.ModelSerializer):
    """Serializer for District model"""
    
    class Meta:
        model = District
        fields = ['district_id', 'city_name', 'district_name', 'max_agencies']
        read_only_fields = ['district_id']


class AgencyListSerializer(serializers.ModelSerializer):
    """Serializer for Agency list view (minimal fields)"""
    id = serializers.IntegerField(source='agency_id', read_only=True)
    code = serializers.SerializerMethodField()
    name = serializers.CharField(source='agency_name', read_only=True)
    type = serializers.CharField(source='agency_type.type_name', read_only=True)
    type_id = serializers.IntegerField(source='agency_type.agency_type_id', read_only=True)
    district = serializers.CharField(source='district.district_name', read_only=True)
    district_id = serializers.IntegerField(source='district.district_id', read_only=True)
    phone = serializers.CharField(source='phone_number', read_only=True)
    address = serializers.CharField(read_only=True)
    email = serializers.CharField(read_only=True)
    current_debt = serializers.DecimalField(source='debt_amount', max_digits=15, decimal_places=2, read_only=True)
    debt_limit = serializers.SerializerMethodField()
    is_active = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    
    class Meta:
        model = Agency
        fields = [
            'id', 'code', 'name', 'type', 'type_id', 'district', 'district_id',
            'address', 'phone', 'email', 'current_debt', 'debt_limit', 'is_active',
            'created_at', 'updated_at'
        ]
    
    def get_code(self, obj):
        """Generate a code based on agency_id"""
        return f"DL{obj.agency_id:03d}"
    
    def get_debt_limit(self, obj):
        """Get debt limit from agency type"""
        return obj.agency_type.max_debt if obj.agency_type else 0
    
    def get_is_active(self, obj):
        """For now, assume all agencies are active - can be updated later"""
        return True


class AgencyDetailSerializer(serializers.ModelSerializer):
    """Serializer for Agency detail view (full fields)"""
    id = serializers.IntegerField(source='agency_id', read_only=True)
    code = serializers.SerializerMethodField()
    name = serializers.CharField(source='agency_name')
    type = serializers.CharField(source='agency_type.type_name', read_only=True)
    type_id = serializers.IntegerField(source='agency_type.agency_type_id')
    district = serializers.CharField(source='district.district_name', read_only=True)
    district_id = serializers.IntegerField(source='district.district_id')
    phone = serializers.CharField(source='phone_number')
    address = serializers.CharField()
    email = serializers.CharField(allow_blank=True, allow_null=True)
    representative = serializers.CharField(allow_blank=True, allow_null=True)
    current_debt = serializers.DecimalField(source='debt_amount', max_digits=15, decimal_places=2, read_only=True)
    debt_limit = serializers.DecimalField(source='agency_type.max_debt', max_digits=15, decimal_places=2, read_only=True)
    is_active = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    
    class Meta:
        model = Agency
        fields = [
            'id', 'code', 'name', 'type', 'type_id', 'district', 'district_id',
            'address', 'phone', 'email', 'representative', 'current_debt', 'debt_limit', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'code', 'type', 'district', 'current_debt', 'debt_limit', 'is_active', 'created_at', 'updated_at']
    
    def get_code(self, obj):
        """Generate a code based on agency_id"""
        return f"DL{obj.agency_id:03d}"
    
    def get_is_active(self, obj):
        """For now, assume all agencies are active - can be updated later"""
        return True
    
    def validate_type_id(self, value):
        """Validate agency type exists"""
        if not AgencyType.objects.filter(agency_type_id=value).exists():
            raise serializers.ValidationError("Agency type does not exist.")
        return value
    
    def validate_district_id(self, value):
        """Validate district exists"""
        if not District.objects.filter(district_id=value).exists():
            raise serializers.ValidationError("District does not exist.")
        return value
    
    def update(self, instance, validated_data):
        """Update agency with proper field mapping - does NOT modify AgencyType.max_debt"""
        # Direct field updates - using the source mapping
        if 'agency_name' in validated_data:
            instance.agency_name = validated_data['agency_name']
        if 'phone_number' in validated_data:
            instance.phone_number = validated_data['phone_number']
        if 'address' in validated_data:
            instance.address = validated_data['address']
        if 'email' in validated_data:
            instance.email = validated_data['email']
        if 'representative' in validated_data:
            instance.representative = validated_data['representative']
        
        # Handle agency type update - ONLY change the reference, NOT the AgencyType.max_debt
        agency_type_data = validated_data.get('agency_type', {})
        agency_type_id = agency_type_data.get('agency_type_id')
        if agency_type_id:
            # Update agency type reference - debt limit will be automatically reflected via the relationship
            new_agency_type = AgencyType.objects.get(agency_type_id=agency_type_id)
            instance.agency_type = new_agency_type
            # Note: We do NOT modify new_agency_type.max_debt - it remains unchanged
        
        # Handle district update
        district_data = validated_data.get('district', {})
        district_id = district_data.get('district_id')
        if district_id:
            instance.district = District.objects.get(district_id=district_id)
        
        instance.save()
        return instance


class AgencyCreateSerializer(serializers.ModelSerializer):
    """Serializer for Agency creation (registration flow)"""
    # Use frontend field names
    name = serializers.CharField(source='agency_name', max_length=150, required=True)
    phone = serializers.CharField(source='phone_number', max_length=15, required=True)
    address = serializers.CharField(max_length=255, required=True)
    email = serializers.EmailField(max_length=100, required=False, allow_blank=True, allow_null=True)
    type_id = serializers.IntegerField(write_only=True, required=True)
    district_id = serializers.IntegerField(write_only=True, required=True)
    
    class Meta:
        model = Agency
        fields = [
            'name', 'phone', 'address', 'email', 'type_id', 'district_id'
        ]
    
    def validate_type_id(self, value):
        """Validate agency type exists"""
        if not AgencyType.objects.filter(agency_type_id=value).exists():
            raise serializers.ValidationError("Agency type does not exist.")
        return value
    
    def validate_district_id(self, value):
        """Validate district exists and has capacity"""
        try:
            district = District.objects.get(district_id=value)
            current_count = Agency.objects.filter(district_id=value).count()
            if current_count >= district.max_agencies:
                raise serializers.ValidationError(
                    f"District has reached maximum capacity ({district.max_agencies} agencies)."
                )
        except District.DoesNotExist:
            raise serializers.ValidationError("District does not exist.")
        return value
    
    def validate_phone(self, value):
        """Validate phone number format per DDL constraint VARCHAR(15)"""
        if not value.replace('+', '').replace('-', '').replace(' ', '').isdigit():
            raise serializers.ValidationError("Phone number must contain only digits, spaces, hyphens, or plus sign.")
        if len(value) > 15:
            raise serializers.ValidationError("Phone number cannot exceed 15 characters.")
        return value
    
    def create(self, validated_data):
        """Create agency with default values per DDL.sql"""
        from django.utils import timezone
        from datetime import date
        
        # Map frontend fields to model fields
        agency_name = validated_data.pop('agency_name')
        phone_number = validated_data.pop('phone_number')
        
        # Map ID fields to actual foreign key instances
        type_id = validated_data.pop('type_id')
        district_id = validated_data.pop('district_id')
        
        agency_type = AgencyType.objects.get(agency_type_id=type_id)
        district = District.objects.get(district_id=district_id)
        
        # Create agency with proper field mapping
        agency = Agency.objects.create(
            agency_name=agency_name,
            phone_number=phone_number,
            address=validated_data.get('address'),
            email=validated_data.get('email'),
            agency_type=agency_type,
            district=district,
            debt_amount=0,  # DEFAULT 0 per DDL
            reception_date=date.today(),  # Set to today
            created_at=timezone.now()  # DEFAULT CURRENT_TIMESTAMP
        )
        
        return agency


class StaffAgencySerializer(serializers.ModelSerializer):
    """Serializer for StaffAgency model - NO id field, composite PK per DDL.sql"""
    agency_name = serializers.CharField(source='agency.agency_name', read_only=True)
    
    class Meta:
        model = StaffAgency
        # Note: No 'id' field - DDL.sql uses composite PK (staff_id, agency_id)
        fields = ['staff_id', 'agency', 'agency_name']
        
    def validate(self, attrs):
        """Validate unique staff-agency pair per DDL.sql PRIMARY KEY constraint"""
        staff_id = attrs.get('staff_id')
        agency = attrs.get('agency')
        
        if StaffAgency.objects.filter(staff_id=staff_id, agency=agency).exists():
            raise serializers.ValidationError("This staff-agency relationship already exists.")
        
        return attrs 