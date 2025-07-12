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


# ========================================
# AGENCY APPROVAL PROCESS SERIALIZERS  
# ========================================

class AgencyRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for agency self-registration (public form)
    Creates agency with user_id = NULL (pending approval)
    """
    agency_name = serializers.CharField(max_length=150, help_text="Tên đại lý")
    phone_number = serializers.CharField(max_length=15, help_text="Số điện thoại")
    address = serializers.CharField(max_length=255, help_text="Địa chỉ")
    email = serializers.EmailField(max_length=100, required=False, allow_blank=True, help_text="Email liên hệ")
    representative = serializers.CharField(max_length=100, required=False, allow_blank=True, help_text="Người đại diện")
    agency_type_id = serializers.IntegerField(help_text="ID loại đại lý")
    district_id = serializers.IntegerField(help_text="ID quận/huyện")
    
    class Meta:
        model = Agency
        fields = [
            'agency_name', 'phone_number', 'address', 'email', 'representative',
            'agency_type_id', 'district_id'
        ]
    
    def validate_agency_type_id(self, value):
        """Validate agency type exists"""
        if not AgencyType.objects.filter(agency_type_id=value).exists():
            raise serializers.ValidationError("Loại đại lý không tồn tại.")
        return value
    
    def validate_district_id(self, value):
        """Validate district exists and has capacity"""
        try:
            district = District.objects.get(district_id=value)
            current_count = Agency.objects.filter(district_id=value).count()
            if current_count >= district.max_agencies:
                raise serializers.ValidationError(
                    f"Quận/huyện đã đạt giới hạn số lượng đại lý ({district.max_agencies} đại lý)."
                )
        except District.DoesNotExist:
            raise serializers.ValidationError("Quận/huyện không tồn tại.")
        return value
    
    def validate_phone_number(self, value):
        """Validate phone number format per DDL constraint VARCHAR(15)"""
        # Remove common formatting characters for validation
        clean_phone = value.replace('+', '').replace('-', '').replace(' ', '').replace('(', '').replace(')', '')
        if not clean_phone.isdigit():
            raise serializers.ValidationError("Số điện thoại chỉ được chứa số và ký tự định dạng.")
        if len(value) > 15:
            raise serializers.ValidationError("Số điện thoại không được vượt quá 15 ký tự.")
        return value
    
    def validate_email(self, value):
        """Validate email uniqueness if provided"""
        if value and Agency.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email này đã được đăng ký bởi đại lý khác.")
        return value
    
    def create(self, validated_data):
        """
        Create agency with user_id = NULL (pending approval)
        Following DDL constraints and business rules
        """
        from django.utils import timezone
        from datetime import date
        
        # Get related objects
        agency_type = AgencyType.objects.get(agency_type_id=validated_data.pop('agency_type_id'))
        district = District.objects.get(district_id=validated_data.pop('district_id'))
        
        # Create agency with DDL-compliant fields
        agency = Agency.objects.create(
            agency_name=validated_data['agency_name'],
            phone_number=validated_data['phone_number'],
            address=validated_data['address'],
            email=validated_data.get('email') or None,  # NULL if empty per DDL
            representative=validated_data.get('representative') or None,  # NULL if empty per DDL
            agency_type=agency_type,
            district=district,
            reception_date=date.today(),  # NOT NULL per DDL
            debt_amount=0,  # DEFAULT 0 per DDL
            user_id=None,  # KEY: NULL = pending approval
            created_at=timezone.now()  # DEFAULT CURRENT_TIMESTAMP per DDL
        )
        
        return agency


class AgencyPendingSerializer(serializers.ModelSerializer):
    """
    Serializer for listing agencies pending approval
    Only agencies with user_id = NULL
    """
    id = serializers.IntegerField(source='agency_id', read_only=True)
    code = serializers.SerializerMethodField()
    name = serializers.CharField(source='agency_name', read_only=True)
    type = serializers.CharField(source='agency_type.type_name', read_only=True)
    type_id = serializers.IntegerField(source='agency_type.agency_type_id', read_only=True)
    district = serializers.CharField(source='district.district_name', read_only=True)
    district_id = serializers.IntegerField(source='district.district_id', read_only=True)
    city = serializers.CharField(source='district.city_name', read_only=True)
    phone = serializers.CharField(source='phone_number', read_only=True)
    address = serializers.CharField(read_only=True)
    email = serializers.CharField(read_only=True)
    representative = serializers.CharField(read_only=True)
    registration_date = serializers.DateField(source='reception_date', read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    days_pending = serializers.SerializerMethodField()
    
    class Meta:
        model = Agency
        fields = [
            'id', 'code', 'name', 'type', 'type_id', 'district', 'district_id', 'city',
            'address', 'phone', 'email', 'representative', 'registration_date', 
            'created_at', 'days_pending'
        ]
    
    def get_code(self, obj):
        """Generate a code based on agency_id"""
        return f"HS{obj.agency_id:04d}"  # HS = Hồ Sơ
    
    def get_days_pending(self, obj):
        """Calculate days since registration"""
        from django.utils import timezone
        if obj.created_at:
            delta = timezone.now().date() - obj.created_at.date()
            return delta.days
        return 0


class AgencyApprovalSerializer(serializers.Serializer):
    """
    Serializer for approving agency and creating user account
    Input: username, password for new account
    """
    username = serializers.CharField(
        max_length=50, 
        help_text="Tên đăng nhập cho đại lý",
        error_messages={
            'required': 'Tên đăng nhập là bắt buộc.',
            'max_length': 'Tên đăng nhập không được vượt quá 50 ký tự.'
        }
    )
    password = serializers.CharField(
        max_length=255, 
        write_only=True,
        help_text="Mật khẩu cho đại lý",
        error_messages={
            'required': 'Mật khẩu là bắt buộc.'
        }
    )
    full_name = serializers.CharField(
        max_length=100, 
        required=False, 
        help_text="Họ tên đầy đủ (mặc định dùng tên đại lý)"
    )
    
    def validate_username(self, value):
        """Validate username uniqueness per DDL UNIQUE constraint"""
        from authentication.models import Account
        if Account.objects.filter(username=value).exists():
            raise serializers.ValidationError("Tên đăng nhập đã tồn tại.")
        
        # Basic username validation
        if not value.replace('_', '').replace('.', '').isalnum():
            raise serializers.ValidationError("Tên đăng nhập chỉ được chứa chữ, số, dấu gạch dưới và dấu chấm.")
        
        return value
    
    def validate_password(self, value):
        """Validate password strength"""
        if len(value) < 8:
            raise serializers.ValidationError("Mật khẩu phải có ít nhất 8 ký tự.")
        return value


class AgencyRejectSerializer(serializers.Serializer):
    """
    Serializer for rejecting agency application
    Input: reason for rejection
    """
    reason = serializers.CharField(
        max_length=500,
        help_text="Lý do từ chối hồ sơ",
        error_messages={
            'required': 'Lý do từ chối là bắt buộc.',
            'max_length': 'Lý do từ chối không được vượt quá 500 ký tự.'
        }
    )
    
    # Optional: Send notification email
    send_email = serializers.BooleanField(
        default=True,
        help_text="Gửi email thông báo cho đại lý"
    )


class AgencyAssignmentSerializer(serializers.Serializer):
    """
    Serializer for assigning agency profile to existing agent user
    Used in /agency/assign-profile/ endpoint
    """
    user_id = serializers.IntegerField(min_value=1)
    agency_name = serializers.CharField(max_length=150)
    agency_type_id = serializers.IntegerField(min_value=1)
    district_id = serializers.IntegerField(min_value=1)
    phone_number = serializers.CharField(max_length=15)
    address = serializers.CharField(max_length=255)
    email = serializers.EmailField(required=False, allow_blank=True)
    representative = serializers.CharField(max_length=100, required=False, allow_blank=True)
    
    def validate_agency_name(self, value):
        """Validate agency name is not empty"""
        if not value.strip():
            raise serializers.ValidationError("Tên đại lý không được để trống.")
        return value.strip()
    
    def validate_phone_number(self, value):
        """Validate phone number format"""
        import re
        if not re.match(r'^\d{10,15}$', value):
            raise serializers.ValidationError("Số điện thoại phải từ 10-15 chữ số.")
        return value
    
    def validate_address(self, value):
        """Validate address is not empty"""
        if not value.strip():
            raise serializers.ValidationError("Địa chỉ không được để trống.")
        return value.strip()