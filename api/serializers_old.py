from rest_framework import serializers
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import models, transaction
from Core.models import (
    Currency, Province, SarafProfile, SupportedCurrency, 
    sendhawala, ReceiveHawala, 
    CustomerTransaction, SarafColleague, SarafLoan, CurrencyExchange,
    Message, MessageAttachment, normal_user_Profile, CustomerAccount, CustomerBalance
)

class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = ['id', 'code', 'name', 'name_english', 'name_farsi', 'symbol', 'is_active', 'is_default', 'exchange_rate']

class ProvinceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Province
        fields = ['name']

# ServiceSerializer removed - Service model not found

class SupportedCurrencySerializer(serializers.ModelSerializer):
    currency = CurrencySerializer(read_only=True)
    currency_symbol = serializers.CharField(write_only=True, required=False, help_text='Currency symbol, e.g., $, € , ₨, ₹, ﷼, ¥, £')
    currency_code = serializers.CharField(write_only=True, required=False, help_text='ISO code, e.g., USD, AFN, IRR, PKR')
    currency_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = SupportedCurrency
        fields = ['id', 'currency', 'currency_id', 'currency_symbol', 'currency_code', 'created_at']

    def _resolve_currency(self, attrs):
        # Prefer code, then symbol, then id
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

    def update(self, instance, validated_data):
        if any(k in validated_data for k in ['currency_code', 'currency_symbol', 'currency_id']):
            currency = self._resolve_currency(validated_data)
            validated_data['currency'] = currency
        return super().update(instance, validated_data)

class sendhawalaSerializer(serializers.ModelSerializer):
    currency = CurrencySerializer(read_only=True)
    currency_symbol = serializers.CharField(write_only=True, required=False)
    currency_code = serializers.CharField(write_only=True, required=False)
    currency_id = serializers.IntegerField(write_only=True, required=False)
    hawala_fee_currency = CurrencySerializer(read_only=True)
    hawala_fee_currency_symbol = serializers.CharField(write_only=True, required=False)
    hawala_fee_currency_code = serializers.CharField(write_only=True, required=False)
    hawala_fee_currency_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = sendhawala
        fields = [
            'send_hawala_id', 'hawala_number', 'sender_name', 'receiver_name',
            'amount', 'currency', 'currency_id', 'currency_symbol', 'currency_code', 'receiver_location',
            'exchanger_location', 'sender_phone', 'hawala_fee', 'hawala_fee_currency',
            'hawala_fee_currency_id', 'hawala_fee_currency_symbol', 'hawala_fee_currency_code', 'dates', 'status'
        ]
        read_only_fields = ['send_hawala_id', 'dates']

    def _resolve_currency(self, data, id_key, code_key, symbol_key, default_ok=False):
        cid = data.pop(id_key, None)
        code = data.pop(code_key, None)
        symbol = data.pop(symbol_key, None)
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
                raise serializers.ValidationError({symbol_key: 'Ambiguous symbol. Provide currency_code.'})
            return qs.first()
        if cid is not None:
            try:
                return Currency.objects.get(id=cid, is_active=True)
            except Currency.DoesNotExist:
                raise serializers.ValidationError({id_key: 'Invalid or inactive currency id'})
        if default_ok:
            default_currency = Currency.get_default_currency()
            if default_currency:
                return default_currency
        raise serializers.ValidationError({code_key: 'Provide currency_code or currency_symbol'})

    def create(self, validated_data):
        currency = self._resolve_currency(validated_data, 'currency_id', 'currency_code', 'currency_symbol', default_ok=True)
        fee_currency = self._resolve_currency(validated_data, 'hawala_fee_currency_id', 'hawala_fee_currency_code', 'hawala_fee_currency_symbol', default_ok=True)
        validated_data['currency'] = currency
        validated_data['hawala_fee_currency'] = fee_currency
        return super().create(validated_data)

class SarafProfileReadSerializer(serializers.ModelSerializer):
    """Read-only serializer for SarafProfile (excludes password_hash)"""
    supported_currencies = SupportedCurrencySerializer(many=True, read_only=True)
    provinces = ProvinceSerializer(many=True, read_only=True)
    # services = ServiceSerializer(many=True, read_only=True)  # Removed - Service model not found
    balances = serializers.SerializerMethodField()
    
    class Meta:
        model = SarafProfile
        fields = [
            'saraf_id', 'name', 'last_name', 'phone', 'email', 'license_no', 'exchange_name',
            'saraf_address', 'provinces', 'about_us', 'work_history',
            'created_at', 'updated_at', 'is_active', 'saraf_logo',
            'saraf_logo_wallpeper', 'licence_photo', 'supported_currencies', 'balances'
        ]
        read_only_fields = ['saraf_id', 'created_at', 'updated_at']

    def get_balances(self, obj):
        # SarafBalance functionality removed
        return []


class SarafProfileLiteSerializer(serializers.ModelSerializer):
    """Lightweight serializer for SarafProfile list view"""
    class Meta:
        model = SarafProfile
        fields = ['saraf_id', 'exchange_name', 'saraf_address', 'saraf_logo']
        read_only_fields = fields


class SarafProfileLoginSerializer(serializers.Serializer):
    """Serializer for SarafProfile login - supports both email and phone number"""
    email = serializers.EmailField(required=False)
    phone = serializers.CharField(required=False, max_length=15)
    password = serializers.CharField(write_only=True)
    
    def validate_phone(self, value):
        """Validate phone number format"""
        if value:
            import re
            if not re.match(r'^0\d{9}$', value):
                raise serializers.ValidationError('Phone must be 10 digits and start with 0')
        return value
    
    def validate(self, attrs):
        email = attrs.get('email')
        phone = attrs.get('phone')
        password = attrs.get('password')
        
        # Ensure either email or phone is provided
        if not email and not phone:
            raise serializers.ValidationError('Either email or phone number is required')
        
        if email and phone:
            raise serializers.ValidationError('Provide either email or phone number, not both')
        
        if not password:
            raise serializers.ValidationError('Password is required')
        
        # Try to find user by email or phone
        try:
            if email:
                saraf_profile = SarafProfile.objects.get(email=email, is_active=True)
            else:  # phone
                saraf_profile = SarafProfile.objects.get(phone=phone, is_active=True)
                
            if not saraf_profile.check_password(password):
                raise serializers.ValidationError('Invalid login credentials')
            attrs['saraf_profile'] = saraf_profile
        except SarafProfile.DoesNotExist:
            raise serializers.ValidationError('Invalid login credentials')
        
        return attrs


class SarafProfileDualLoginSerializer(serializers.Serializer):
    """Serializer for SarafProfile dual login - requires both email and phone number"""
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=15)
    password = serializers.CharField(write_only=True)
    
    def validate_phone(self, value):
        """Validate phone number format"""
        import re
        if not re.match(r'^0\d{9}$', value):
            raise serializers.ValidationError('Phone must be 10 digits and start with 0')
        return value
    
    def validate(self, attrs):
        email = attrs.get('email')
        phone = attrs.get('phone')
        password = attrs.get('password')
        
        if not password:
            raise serializers.ValidationError('Password is required')
        
        # Find user that matches both email AND phone
        try:
            saraf_profile = SarafProfile.objects.get(
                email=email, 
                phone=phone, 
                is_active=True
            )
            
            if not saraf_profile.check_password(password):
                raise serializers.ValidationError('Invalid login credentials')
            attrs['saraf_profile'] = saraf_profile
        except SarafProfile.DoesNotExist:
            raise serializers.ValidationError('Invalid login credentials - email and phone must match the same account')
        
        return attrs


class SarafProfileSerializer(serializers.ModelSerializer):
    """Full serializer for SarafProfile creation and updates"""
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    # Deprecated single-currency inputs (kept for backward compatibility)
    currency_symbol = serializers.CharField(write_only=True, required=False, help_text='Deprecated: initial supported currency symbol (e.g., $, € , ₨, ₹, ﷼, ¥, £)')
    currency_code = serializers.CharField(write_only=True, required=False, help_text='Deprecated: provide ISO code (e.g., AFN, IRR, USD, PKR)')
    provinces = ProvinceSerializer(many=True, read_only=True)
    # services = ServiceSerializer(many=True, read_only=True)  # Removed - Service model not found
    province_names = serializers.ListField(child=serializers.CharField(), write_only=True, required=False, allow_empty=True)
    service_ids = serializers.ListField(child=serializers.IntegerField(), write_only=True, required=False, allow_empty=True)
    currency_id = serializers.IntegerField(write_only=True, required=False, help_text='Deprecated: prefer supported_currencies')
    # New multi-choice input for supported currencies
    supported_currencies_input = SupportedCurrencySerializer(many=True, write_only=True, required=False, help_text='List of supported currencies, e.g., [{"currency_code":"USD"},{"currency_code":"AFN"}]')
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
        from django.db import transaction
        
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
                    validated_currencies.append(sc_ser.validated_data)
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
    
    def validate_from_currency_id(self, value):
        if value:
            try:
                Currency.objects.get(id=value, is_active=True)
            except Currency.DoesNotExist:
                raise serializers.ValidationError("From currency not found or inactive")
        return value
    
    def validate_to_currency_id(self, value):
        if value:
            try:
                Currency.objects.get(id=value, is_active=True)
            except Currency.DoesNotExist:
                raise serializers.ValidationError("To currency not found or inactive")
        return value
    
    def create(self, validated_data):
        from django.db import transaction
        
        receiver_id = validated_data.pop('receiver_id')
        from_currency_code = validated_data.pop('from_currency_code', None)
        from_currency_id = validated_data.pop('from_currency_id', None)
        from_currency_symbol = validated_data.pop('from_currency_symbol', None)
        to_currency_code = validated_data.pop('to_currency_code', None)
        to_currency_id = validated_data.pop('to_currency_id', None)
        to_currency_symbol = validated_data.pop('to_currency_symbol', None)
        
        # Get receiver (SarafProfile)
        try:
            receiver = SarafProfile.objects.get(saraf_id=receiver_id, is_active=True)
        except SarafProfile.DoesNotExist:
            raise serializers.ValidationError("Receiver not found or inactive")
        
        # Get sender from session
        request = self.context['request']
        sender_id = request.session.get('user_id')
        try:
            sender = SarafProfile.objects.get(saraf_id=sender_id)
        except SarafProfile.DoesNotExist:
            raise serializers.ValidationError("Invalid sender")
        
        # Resolve from_currency
        from_currency = None
        if from_currency_code:
            try:
                from_currency = Currency.objects.get(code__iexact=from_currency_code, is_active=True)
            except Currency.DoesNotExist:
                raise serializers.ValidationError("From currency not found or inactive")
        elif from_currency_symbol:
            qs = Currency.objects.filter(symbol=from_currency_symbol, is_active=True)
            if not qs.exists():
                raise serializers.ValidationError("From currency not found or inactive")
            if qs.count() > 1:
                raise serializers.ValidationError("Ambiguous from currency symbol. Use from_currency_code instead.")
            from_currency = qs.first()
        elif from_currency_id is not None:
            try:
                from_currency = Currency.objects.get(id=from_currency_id, is_active=True)
            except Currency.DoesNotExist:
                raise serializers.ValidationError("From currency not found or inactive")
            from_currency = Currency.objects.get(code=from_currency_code)
        else:
            from_currency = Currency.objects.get(id=from_currency_id)
            
        if to_currency_code:
            to_currency = Currency.objects.get(code=to_currency_code)
        else:
            to_currency = Currency.objects.get(id=to_currency_id)
        
        return CurrencyExchange.objects.create(
            exchanger=exchanger,
            receiver=receiver,
            from_currency=from_currency,
            to_currency=to_currency,
            **validated_data
        )


class SarafLoanRepaySerializer(serializers.Serializer):
    """Serializer for loan repayment"""
    loan_id = serializers.IntegerField()
    
    def validate_loan_id(self, value):
        """Validate that the loan exists and can be repaid"""
        try:
            loan = SarafLoan.objects.get(id=value)
            if loan.status != 'active':
                raise serializers.ValidationError("Only active loans can be repaid")
            return loan
        except SarafLoan.DoesNotExist:
            raise serializers.ValidationError("Loan not found")


class NormalUserProfileSerializer(serializers.ModelSerializer):
    """Full serializer for NormalUserProfile creation and updates"""
    password = serializers.CharField(write_only=True)
    preferred_currency = CurrencySerializer(read_only=True)
    preferred_currency_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = normal_user_Profile
        fields = [
            'normal_user_id', 'name', 'last_name', 'phone', 'email', 'password',
            'preferred_currency', 'preferred_currency_id', 'created_at', 'updated_at'
        ]
        read_only_fields = ['normal_user_id', 'created_at', 'updated_at']
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def create(self, validated_data):
        from django.db import transaction
        
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
    
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            try:
                instance.set_password(password)
            except DjangoValidationError:
                raise serializers.ValidationError({
                    'password': {
                        'error': 'Password does not meet security requirements',
                        'requirements': instance.get_password_requirements()
                    }
                })
        instance.save()
        return instance


class NormalUserProfileReadSerializer(serializers.ModelSerializer):
    """Read-only serializer for NormalUserProfile (excludes password_hash)"""
    preferred_currency = CurrencySerializer(read_only=True)
    
    class Meta:
        model = normal_user_Profile
        fields = [
            'normal_user_id', 'name', 'last_name', 'phone', 'email',
            'preferred_currency', 'created_at', 'updated_at'
        ]
        read_only_fields = ['normal_user_id', 'created_at', 'updated_at']


class NormalUserProfileLoginSerializer(serializers.Serializer):
    """Serializer for NormalUserProfile login"""
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            try:
                normal_user_profile = normal_user_Profile.objects.get(email=email)
                if not normal_user_profile.check_password(password):
                    raise serializers.ValidationError('Invalid login credentials')
                attrs['normal_user_profile'] = normal_user_profile
            except normal_user_Profile.DoesNotExist:
                raise serializers.ValidationError('Invalid login credentials')
        else:
            raise serializers.ValidationError('Email and password are required')
        
        return attrs