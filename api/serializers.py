from rest_framework import serializers
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import models, transaction
from Core.models import (
    Currency, Province, SarafProfile, SupportedCurrency, 
    sendhawala, ReceiveHawala, 
    CustomerTransaction, SarafColleague, SarafLoan, CurrencyExchange,
    Message, MessageAttachment, normal_user_Profile, CustomerAccount, CustomerBalance,
    SarafPost,
)

class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = ['id', 'code', 'name', 'name_english', 'name_farsi', 'symbol', 'is_active', 'is_default', 'exchange_rate']

class ProvinceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Province
        fields = ['name']

class SupportedCurrencySerializer(serializers.ModelSerializer):
    currency = CurrencySerializer(read_only=True)
    currency_symbol = serializers.CharField(write_only=True, required=False)
    currency_code = serializers.CharField(write_only=True, required=False)
    currency_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = SupportedCurrency
        fields = ['id', 'currency', 'currency_id', 'currency_symbol', 'currency_code', 'created_at']

    def _resolve_currency(self, attrs):
        code = attrs.pop('currency_code', None)
        symbol = attrs.pop('currency_symbol', None)
        cid = attrs.pop('currency_id', None)
        if code:
            try:
                return Currency.objects.get(code__iexact=code, is_active=True)
            except Currency.DoesNotExist:
                raise serializers.ValidationError({'currency_code': 'Invalid or inactive currency code'})
        if symbol:
            qs = Currency.objects.filter(symbol=symbol, is_active=True)
            if not qs.exists():
                raise serializers.ValidationError({'currency_symbol': 'Invalid or inactive currency symbol'})
            if qs.count() > 1:
                raise serializers.ValidationError({'currency_symbol': 'Ambiguous symbol. Provide currency_code to disambiguate.'})
            return qs.first()
        if cid is not None:
            try:
                return Currency.objects.get(id=cid, is_active=True)
            except Currency.DoesNotExist:
                raise serializers.ValidationError({'currency_id': 'Invalid or inactive currency id'})
        raise serializers.ValidationError({'currency_code': 'Provide currency_code or currency_symbol'})

    def create(self, validated_data):
        currency = self._resolve_currency(validated_data)
        validated_data['currency'] = currency
        return super().create(validated_data)

class sendhawalaSerializer(serializers.ModelSerializer):
    currency_code = serializers.CharField(write_only=True, required=False)
    currency_symbol = serializers.CharField(write_only=True, required=False)
    currency_id = serializers.IntegerField(write_only=True, required=False)
    hawala_fee_currency_code = serializers.CharField(write_only=True, required=False)
    hawala_fee_currency_symbol = serializers.CharField(write_only=True, required=False)
    hawala_fee_currency_id = serializers.IntegerField(write_only=True, required=False)
    currency = CurrencySerializer(read_only=True)
    hawala_fee_currency = CurrencySerializer(read_only=True)
    
    # Add a custom field for API response that maps to the actual model field
    send_hawala_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = sendhawala
        fields = [
            'send_hawala_id', 'hawala_number', 'sender_name', 'receiver_name', 'amount', 'currency', 'currency_id', 'currency_code', 'currency_symbol',
            'sender_phone', 'receiver_location', 'exchanger_location', 'hawala_fee', 'hawala_fee_currency', 'hawala_fee_currency_id', 'hawala_fee_currency_code', 'hawala_fee_currency_symbol',
            'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['send_hawala_id', 'hawala_number', 'created_at', 'updated_at']
        
    def validate(self, data):
        """Add validation for required fields"""
        required_fields = ['sender_name', 'receiver_name', 'amount', 'sender_phone', 'receiver_location', 'exchanger_location']
        for field in required_fields:
            if not data.get(field):
                raise serializers.ValidationError({field: f'{field} is required'})
        
        # Validate amount is positive
        if data.get('amount') and data['amount'] <= 0:
            raise serializers.ValidationError({'amount': 'Amount must be greater than 0'})
            
        # Validate hawala_fee is positive if provided
        if data.get('hawala_fee') and data['hawala_fee'] < 0:
            raise serializers.ValidationError({'hawala_fee': 'Hawala fee cannot be negative'})
            
        return data

    def _resolve_currency(self, validated_data, code_key, symbol_key, id_key, default_ok=False):
        code = validated_data.pop(code_key, None)
        symbol = validated_data.pop(symbol_key, None)
        cid = validated_data.pop(id_key, None)
        if code:
            try:
                return Currency.objects.get(code__iexact=code, is_active=True)
            except Currency.DoesNotExist:
                raise serializers.ValidationError({code_key: 'Invalid or inactive currency code'})
        if symbol:
            qs = Currency.objects.filter(symbol=symbol, is_active=True)
            if not qs.exists():
                raise serializers.ValidationError({symbol_key: 'Invalid or inactive currency symbol'})
            if qs.count() > 1:
                raise serializers.ValidationError({symbol_key: 'Ambiguous symbol. Provide currency_code to disambiguate.'})
            return qs.first()
        if cid is not None:
            try:
                return Currency.objects.get(id=cid, is_active=True)
            except Currency.DoesNotExist:
                raise serializers.ValidationError({id_key: 'Invalid or inactive currency'})
        if default_ok:
            default_currency = Currency.get_default_currency()
            if default_currency:
                return default_currency
        raise serializers.ValidationError({code_key: 'Provide currency_code or currency_symbol'})

    def create(self, validated_data):
        with transaction.atomic():
            try:
                currency = self._resolve_currency(validated_data, 'currency_code', 'currency_symbol', 'currency_id', default_ok=True)
                fee_currency = self._resolve_currency(validated_data, 'hawala_fee_currency_code', 'hawala_fee_currency_symbol', 'hawala_fee_currency_id', default_ok=True)
                validated_data['currency'] = currency
                validated_data['hawala_fee_currency'] = fee_currency
                return super().create(validated_data)
            except Exception as e:
                raise serializers.ValidationError({'error': f'Failed to create hawala: {str(e)}'})

class SarafProfileSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    province_names = serializers.ListField(child=serializers.CharField(), write_only=True, required=False, allow_empty=True)
    supported_currencies_input = SupportedCurrencySerializer(many=True, write_only=True, required=False)
    currency_id = serializers.IntegerField(write_only=True, required=False)
    currency_symbol = serializers.CharField(write_only=True, required=False)
    currency_code = serializers.CharField(write_only=True, required=False)
    service_ids = serializers.ListField(child=serializers.IntegerField(), write_only=True, required=False, allow_empty=True)
    provinces = ProvinceSerializer(many=True, read_only=True)
    supported_currencies = SupportedCurrencySerializer(many=True, read_only=True)
    
    class Meta:
        model = SarafProfile
        fields = [
            'saraf_id', 'name', 'last_name', 'phone', 'email', 'password', 'confirm_password', 'license_no', 'exchange_name',
            'saraf_address', 'provinces', 'province_names', 'service_ids', 'about_us', 'work_history', 'currency_id', 'currency_symbol', 'currency_code', 'supported_currencies_input',
            'created_at', 'updated_at', 'is_active', 'saraf_logo',
            'saraf_logo_wallpeper', 'licence_photo', 'supported_currencies'
        ]
        read_only_fields = ['saraf_id', 'created_at', 'updated_at']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password')
        confirm_password = validated_data.pop('confirm_password', None)
        currency_id = validated_data.pop('currency_id', None)
        currency_code = validated_data.pop('currency_code', None)
        currency_symbol = validated_data.pop('currency_symbol', None)
        supported_currencies_input = validated_data.pop('supported_currencies_input', None)
        province_names = validated_data.pop('province_names', [])
        service_ids = validated_data.pop('service_ids', [])
        
        # Validate before any database operations
        if confirm_password is None or password != confirm_password:
            raise serializers.ValidationError({'confirm_password': 'Passwords do not match'})
        
        # Validate provinces before creating profile
        resolved_province_ids = []
        if province_names:
            missing = []
            for n in province_names:
                try:
                    p = Province.objects.get(name__iexact=n, is_active=True)
                    resolved_province_ids.append(p.id)
                except Province.DoesNotExist:
                    missing.append(n)
            if missing:
                raise serializers.ValidationError({'province_names': f"Invalid or inactive provinces: {', '.join(missing)}"})
        
        # Validate currencies before creating profile
        validated_currencies = []
        if supported_currencies_input:
            errors = []
            for item in supported_currencies_input:
                sc_ser = SupportedCurrencySerializer(data=item)
                if sc_ser.is_valid():
                    # Resolve currency from validated data and store the currency object
                    currency = sc_ser._resolve_currency(sc_ser.validated_data.copy())
                    validated_currencies.append({'currency': currency})
                else:
                    errors.append(sc_ser.errors)
            if errors:
                raise serializers.ValidationError({'supported_currencies_input': errors})
        else:
            # Backward compatible single currency validation
            currency = None
            if currency_code:
                try:
                    currency = Currency.objects.get(code__iexact=currency_code, is_active=True)
                except Currency.DoesNotExist:
                    raise serializers.ValidationError({'currency_code': 'Invalid or inactive currency code.'})
            elif currency_symbol:
                qs = Currency.objects.filter(symbol=currency_symbol, is_active=True)
                if not qs.exists():
                    raise serializers.ValidationError({'currency_symbol': 'Invalid or inactive currency symbol.'})
                if qs.count() > 1:
                    raise serializers.ValidationError({'currency_symbol': 'Ambiguous symbol. Provide currency_code to disambiguate.'})
                currency = qs.first()
            elif currency_id is not None:
                try:
                    currency = Currency.objects.get(id=currency_id, is_active=True)
                except Currency.DoesNotExist:
                    raise serializers.ValidationError({'currency_id': 'Invalid or inactive currency.'})
            else:
                raise serializers.ValidationError({'supported_currencies_input': 'Provide supported_currencies_input (preferred) or a single currency via currency_code/symbol/id'})
            validated_currencies = [{'currency': currency}]
        
        if service_ids:
            raise serializers.ValidationError({'service_ids': 'Provide services after profile creation. Create Service entries owned by this Saraf, then PATCH with service_ids.'})
        
        # All validations passed, now create in transaction
        with transaction.atomic():
            # Create saraf profile
            saraf_profile = SarafProfile(**validated_data)
            saraf_profile.save()
            
            try:
                saraf_profile.set_password(password)
            except DjangoValidationError:
                raise serializers.ValidationError({
                    'password': {
                        'error': 'Password does not meet security requirements',
                        'requirements': saraf_profile.get_password_requirements()
                    }
                })
            
            # Set provinces
            if resolved_province_ids:
                saraf_profile.provinces.set(resolved_province_ids)
            
            # Create supported currencies
            for currency_data in validated_currencies:
                if 'currency' in currency_data:
                    SupportedCurrency.objects.get_or_create(saraf=saraf_profile, currency=currency_data['currency'])
                else:
                    # For new format
                    SupportedCurrency.objects.create(saraf=saraf_profile, **currency_data)
        
        return saraf_profile

# Add minimal required serializers for views.py imports
class SarafProfileReadSerializer(SarafProfileSerializer):
    class Meta(SarafProfileSerializer.Meta):
        read_only_fields = SarafProfileSerializer.Meta.read_only_fields + ['password', 'confirm_password']

class SarafProfileLiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = SarafProfile
        fields = ['saraf_id', 'name', 'last_name', 'exchange_name']

class SarafProfileLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False)
    phone = serializers.CharField(required=False)
    password = serializers.CharField()
    
    def validate(self, data):
        email = data.get('email')
        phone = data.get('phone')
        password = data.get('password')
        
        if not password:
            raise serializers.ValidationError('Password is required')
        
        if not email and not phone:
            raise serializers.ValidationError('Either email or phone is required')
        
        # Try to find user by email or phone
        saraf_profile = None
        
        if email:
            try:
                saraf_profile = SarafProfile.objects.get(email=email, is_active=True)
            except SarafProfile.DoesNotExist:
                pass
        
        if not saraf_profile and phone:
            try:
                saraf_profile = SarafProfile.objects.get(phone=phone, is_active=True)
            except SarafProfile.DoesNotExist:
                pass
        
        if not saraf_profile:
            raise serializers.ValidationError('Invalid credentials')
        
        if not saraf_profile.check_password(password):
            raise serializers.ValidationError('Invalid credentials')
        
        data['saraf_profile'] = saraf_profile
        return data

class SarafProfileDualLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    phone = serializers.CharField()
    password = serializers.CharField()
    
    def validate(self, data):
        email = data.get('email')
        phone = data.get('phone')
        password = data.get('password')
        
        if not email or not phone or not password:
            raise serializers.ValidationError('Email, phone and password are required')
        
        try:
            saraf_profile = SarafProfile.objects.get(
                email=email, 
                phone=phone, 
                is_active=True
            )
        except SarafProfile.DoesNotExist:
            raise serializers.ValidationError('Invalid credentials')
        
        if not saraf_profile.check_password(password):
            raise serializers.ValidationError('Invalid credentials')
        
        data['saraf_profile'] = saraf_profile
        return data

class NormalUserProfileSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    preferred_currency = CurrencySerializer(read_only=True)
    
    class Meta:
        model = normal_user_Profile
        fields = [
            'normal_user_id', 'name', 'last_name', 'phone', 'email', 'password',
            'preferred_currency', 'preferred_currency_id', 'user_logo', 'user_wallpaper',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['normal_user_id', 'created_at', 'updated_at']
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        
        # Validate preferred currency before creating profile
        preferred_currency_id = validated_data.get('preferred_currency_id')
        if preferred_currency_id:
            try:
                Currency.objects.get(id=preferred_currency_id, is_active=True)
            except Currency.DoesNotExist:
                raise serializers.ValidationError({'preferred_currency_id': 'Invalid or inactive currency'})
        else:
            # Set default currency if not provided
            default_currency = Currency.get_default_currency()
            if default_currency:
                validated_data['preferred_currency_id'] = default_currency.id
        
        with transaction.atomic():
            # Create normal user profile
            normal_user_profile = normal_user_Profile(**validated_data)
            normal_user_profile.save()
            
            try:
                normal_user_profile.set_password(password)
            except DjangoValidationError:
                raise serializers.ValidationError({
                    'password': {
                        'error': 'Password does not meet security requirements',
                        'requirements': normal_user_profile.get_password_requirements()
                    }
                })
        
        return normal_user_profile

class NormalUserProfileReadSerializer(NormalUserProfileSerializer):
    class Meta(NormalUserProfileSerializer.Meta):
        read_only_fields = NormalUserProfileSerializer.Meta.read_only_fields + ['password']

class NormalUserProfileLoginSerializer(serializers.Serializer):
    phone = serializers.CharField()
    password = serializers.CharField()
    
    def validate(self, data):
        phone = data.get('phone')
        password = data.get('password')
        
        if not phone or not password:
            raise serializers.ValidationError('Phone and password are required')
        
        try:
            normal_user_profile = normal_user_Profile.objects.get(phone=phone)
        except normal_user_Profile.DoesNotExist:
            raise serializers.ValidationError('Invalid credentials')
        
        if not normal_user_profile.check_password(password):
            raise serializers.ValidationError('Invalid credentials')
        
        data['normal_user_profile'] = normal_user_profile
        return data

class CustomerAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerAccount
        fields = '__all__'

class CustomerAccountCreateSerializer(CustomerAccountSerializer):
    def create(self, validated_data):
        with transaction.atomic():
            return super().create(validated_data)

class CustomerBalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerBalance
        fields = '__all__'

class CustomerTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerTransaction
        fields = '__all__'

class CustomerFinancialOperationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerTransaction
        fields = '__all__'


class BalanceOperationInputSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    currency_id = serializers.IntegerField()

class ReceiveHawalaSerializer(serializers.ModelSerializer):
    sendhawala_details = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = ReceiveHawala
        fields = '__all__'
    
    def get_sendhawala_details(self, obj):
        """Get the related sendhawala details"""
        if obj.sendhawala:
            return sendhawalaSerializer(obj.sendhawala).data
        return None

class ReceiveHawalaCreateSerializer(serializers.ModelSerializer):
    hawala_number = serializers.IntegerField(write_only=True, help_text="Hawala number to fetch sendhawala details")
    
    class Meta:
        model = ReceiveHawala
        fields = [
            'hawala_number', 'receiver_phone', 'receiver_address', 
            'receiver_id_card_photo', 'receiver_finger_photo'
        ]
    
    def validate_hawala_number(self, value):
        """Validate that the hawala_number exists in sendhawala"""
        try:
            sendhawala.objects.get(hawala_number=value)
        except sendhawala.DoesNotExist:
            raise serializers.ValidationError(f"No sendhawala found with hawala_number: {value}")
        return value
    
    def validate(self, data):
        """Additional validation for required fields"""
        required_fields = ['receiver_phone', 'receiver_address']
        for field in required_fields:
            if not data.get(field):
                raise serializers.ValidationError({field: f'{field} is required'})
        return data
    
    def create(self, validated_data):
        hawala_number = validated_data.pop('hawala_number')
        
        with transaction.atomic():
            # Get the sendhawala record
            try:
                send_hawala = sendhawala.objects.get(hawala_number=hawala_number)
            except sendhawala.DoesNotExist:
                raise serializers.ValidationError({
                    'hawala_number': f'No sendhawala found with hawala_number: {hawala_number}'
                })
            
            # Check if ReceiveHawala already exists for this sendhawala
            if hasattr(send_hawala, 'receive_hawala'):
                raise serializers.ValidationError({
                    'hawala_number': f'ReceiveHawala already exists for hawala_number: {hawala_number}'
                })
            
            # Copy sendhawala data to ReceiveHawala
            receive_hawala_data = {
                'sendhawala': send_hawala,
                'hawala_number': str(send_hawala.hawala_number),
                'sender_name': send_hawala.sender_name,
                'receiver_name': send_hawala.receiver_name,
                'amount': send_hawala.amount,
                'currency': send_hawala.currency,
                'sender_phone': send_hawala.sender_phone,
                'hawala_fee': send_hawala.hawala_fee or 0,
                'hawala_fee_currency': send_hawala.hawala_fee_currency,
                'status': send_hawala.status,
                'dates': send_hawala.created_at,
            }
            
            # Handle location fields (convert string to Province if needed)
            if send_hawala.receiver_location:
                try:
                    receiver_location = Province.objects.get(name__iexact=send_hawala.receiver_location, is_active=True)
                    receive_hawala_data['receiver_location'] = receiver_location
                except Province.DoesNotExist:
                    pass  # Keep as None if province not found
            
            if send_hawala.exchanger_location:
                try:
                    exchanger_location = Province.objects.get(name__iexact=send_hawala.exchanger_location, is_active=True)
                    receive_hawala_data['exchanger_location'] = exchanger_location
                except Province.DoesNotExist:
                    pass  # Keep as None if province not found
            
            # Add receiver verification data
            receive_hawala_data.update(validated_data)
            
            # Create ReceiveHawala
            receive_hawala = ReceiveHawala.objects.create(**receive_hawala_data)
            
            return receive_hawala

class MessageAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageAttachment
        fields = '__all__'

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'

class MessageCreateSerializer(serializers.Serializer):
    receiver_id = serializers.IntegerField()
    receiver_type = serializers.ChoiceField(choices=[('saraf', 'Saraf'), ('normal_user', 'Normal User')])
    content = serializers.CharField(required=False, allow_blank=True)
    message_type = serializers.ChoiceField(
        choices=[('text', 'Text'), ('attachment', 'Attachment'), ('mixed', 'Mixed')], 
        default='text'
    )
    attachment_files = serializers.ListField(
        child=serializers.FileField(),
        required=False,
        allow_empty=True
    )
    
    def validate_receiver_id(self, value):
        """Validate that receiver exists"""
        if not value or value <= 0:
            raise serializers.ValidationError("Valid receiver ID is required")
        return value
    
    def validate(self, attrs):
        """Validate receiver exists based on type"""
        receiver_type = attrs.get('receiver_type')
        receiver_id = attrs.get('receiver_id')
        
        if receiver_type == 'saraf':
            try:
                from Core.models import SarafProfile
                SarafProfile.objects.get(saraf_id=receiver_id, is_active=True)
            except SarafProfile.DoesNotExist:
                raise serializers.ValidationError({'receiver_id': 'Saraf not found'})
        elif receiver_type == 'normal_user':
            try:
                from Core.models import normal_user_Profile
                normal_user_Profile.objects.get(normal_user_id=receiver_id)
            except normal_user_Profile.DoesNotExist:
                raise serializers.ValidationError({'receiver_id': 'Normal user not found'})
        
        return attrs

class ConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'

class SarafColleagueSerializer(serializers.ModelSerializer):
    requester_name = serializers.CharField(source='requester.exchange_name', read_only=True)
    colleague_name = serializers.CharField(source='colleague.exchange_name', read_only=True)
    requester_details = serializers.SerializerMethodField(read_only=True)
    colleague_details = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = SarafColleague
        fields = '__all__'
    
    def get_requester_details(self, obj):
        """Get requester saraf details"""
        if obj.requester:
            return {
                'saraf_id': obj.requester.saraf_id,
                'exchange_name': obj.requester.exchange_name,
                'phone': obj.requester.phone,
                'email': obj.requester.email
            }
        return None
    
    def get_colleague_details(self, obj):
        """Get colleague saraf details"""
        if obj.colleague:
            return {
                'saraf_id': obj.colleague.saraf_id,
                'exchange_name': obj.colleague.exchange_name,
                'phone': obj.colleague.phone,
                'email': obj.colleague.email
            }
        return None

class SarafColleagueCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SarafColleague
        fields = ['colleague', 'status']
    
    def validate_colleague(self, value):
        """Validate colleague selection"""
        request = self.context.get('request')
        if not request:
            raise serializers.ValidationError("Request context required")
        
        requester_id = request.session.get('user_id')
        
        # Prevent adding self as colleague
        if value.saraf_id == requester_id:
            raise serializers.ValidationError("Cannot add yourself as a colleague")
        
        # Check if relationship already exists
        if SarafColleague.objects.filter(
            requester_id=requester_id, colleague=value
        ).exists():
            raise serializers.ValidationError("Colleague relationship already exists")
        
        return value
    
    def create(self, validated_data):
        request = self.context.get('request')
        requester_id = request.session.get('user_id')
        
        with transaction.atomic():
            validated_data['requester_id'] = requester_id
            return super().create(validated_data)

class SarafLoanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SarafLoan
        fields = '__all__'

class SarafLoanCreateSerializer(serializers.ModelSerializer):
    currency_code = serializers.CharField(write_only=True, help_text="Currency code (e.g., 'USD', 'AFN')")
    
    class Meta:
        model = SarafLoan
        fields = ['borrower', 'currency_code', 'amount', 'status', 'description']
    
    def validate_currency_code(self, value):
        try:
            Currency.objects.get(code=value, is_active=True)
        except Currency.DoesNotExist:
            raise serializers.ValidationError(f"Currency with code '{value}' not found or inactive")
        return value
    
    def validate_borrower(self, value):
        """Validate that borrower is a colleague of the authenticated user"""
        request = self.context.get('request')
        if not request:
            raise serializers.ValidationError("Request context required")
        
        lender_id = request.session.get('user_id')
        
        # Check if borrower is a colleague
        colleague_exists = SarafColleague.objects.filter(
            models.Q(requester_id=lender_id, colleague=value) |
            models.Q(colleague_id=lender_id, requester=value)
        ).exists()
        
        if not colleague_exists:
            raise serializers.ValidationError("Borrower must be your colleague. Add them first.")
        return value

    def create(self, validated_data):
        request = self.context.get('request')
        if not request:
            raise serializers.ValidationError("Request context required")
        
        lender_id = request.session.get('user_id')
        currency_code = validated_data.pop('currency_code')
        
        with transaction.atomic():
            try:
                currency = Currency.objects.get(code=currency_code, is_active=True)
                validated_data['currency'] = currency
                validated_data['lender_id'] = lender_id
                return super().create(validated_data)
            except Currency.DoesNotExist:
                raise serializers.ValidationError(f"Currency with code '{currency_code}' not found")

class CurrencyExchangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CurrencyExchange
        fields = '__all__'

class CurrencyExchangeCreateSerializer(serializers.ModelSerializer):
    from_currency_code = serializers.CharField(write_only=True, help_text="Source currency code (e.g., 'USD', 'AFN')")
    to_currency_code = serializers.CharField(write_only=True, help_text="Target currency code (e.g., 'USD', 'AFN')")
    
    class Meta:
        model = CurrencyExchange
        fields = ['receiver', 'from_currency_code', 'to_currency_code', 'amount', 'rate', 'status', 'description']
    
    def validate_from_currency_code(self, value):
        try:
            Currency.objects.get(code=value, is_active=True)
        except Currency.DoesNotExist:
            raise serializers.ValidationError(f"From currency with code '{value}' not found or inactive")
        return value
    
    def validate_to_currency_code(self, value):
        try:
            Currency.objects.get(code=value, is_active=True)
        except Currency.DoesNotExist:
            raise serializers.ValidationError(f"To currency with code '{value}' not found or inactive")
        return value
    
    def validate_receiver(self, value):
        """Validate that receiver is a colleague of the authenticated user"""
        request = self.context.get('request')
        if not request:
            raise serializers.ValidationError("Request context required")
        
        exchanger_id = request.session.get('user_id')
        
        # Check if receiver is a colleague
        colleague_exists = SarafColleague.objects.filter(
            models.Q(requester_id=exchanger_id, colleague=value) |
            models.Q(colleague_id=exchanger_id, requester=value)
        ).exists()
        
        if not colleague_exists:
            raise serializers.ValidationError("Receiver must be your colleague. Add them as a colleague first.")
        
        return value
    
    def validate(self, data):
        """Validate that from and to currencies are different"""
        from_currency_code = data.get('from_currency_code')
        to_currency_code = data.get('to_currency_code')
        
        if from_currency_code == to_currency_code:
            raise serializers.ValidationError("From currency and to currency must be different")
        
        return data
    
    def create(self, validated_data):
        request = self.context.get('request')
        if not request:
            raise serializers.ValidationError("Request context required")
        
        exchanger_id = request.session.get('user_id')
        from_currency_code = validated_data.pop('from_currency_code')
        to_currency_code = validated_data.pop('to_currency_code')
        
        with transaction.atomic():
            try:
                from_currency = Currency.objects.get(code=from_currency_code, is_active=True)
                to_currency = Currency.objects.get(code=to_currency_code, is_active=True)
                
                validated_data['from_currency'] = from_currency
                validated_data['to_currency'] = to_currency
                validated_data['exchanger_id'] = exchanger_id
                
                return super().create(validated_data)
            except Currency.DoesNotExist as e:
                raise serializers.ValidationError(f"Currency not found: {str(e)}")

# SarafPost Serializer
class SarafPostSerializer(serializers.ModelSerializer):
    saraf = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = SarafPost
        fields = ['id', 'saraf', 'title', 'content', 'image', 'status', 'is_featured', 'created_at', 'updated_at']
        read_only_fields = ['id', 'saraf', 'created_at', 'updated_at']

    def validate(self, attrs):
        # Enforce at least content or image, mirroring model.clean
        title = attrs.get('title', '')
        content = attrs.get('content', '')
        image = attrs.get('image')
        if not title or not title.strip():
            raise serializers.ValidationError({'title': 'Title is required'})
        if not (content and content.strip()) and not image:
            raise serializers.ValidationError({'content': 'Provide content or an image'})
        return attrs

    def create(self, validated_data):
        request = self.context.get('request')
        if not request:
            raise serializers.ValidationError('Request context required')
        saraf_id = request.session.get('user_id')
        if not saraf_id:
            raise serializers.ValidationError('Authentication required')
        try:
            saraf = SarafProfile.objects.get(saraf_id=saraf_id, is_active=True)
        except SarafProfile.DoesNotExist:
            raise serializers.ValidationError('Authenticated Saraf not found or inactive')
        validated_data['saraf'] = saraf
        return SarafPost.objects.create(**validated_data)
