from django.db import models
from django.contrib.auth.models import User
import uuid
from django.contrib.auth.hashers import make_password, check_password
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
import re
from decimal import Decimal
from django.utils import timezone

class Currency(models.Model):
    """
    Currency model to store available currencies
    """
    code = models.CharField(max_length=3, unique=True, help_text="ISO 4217 currency code (e.g., USD, EUR, GBP)")
    name = models.CharField(max_length=50, help_text="Full currency name (e.g., US Dollar, Euro)")
    name_english = models.CharField(max_length=50, help_text="English currency name", blank=True)
    name_farsi = models.CharField(max_length=50, help_text="Farsi currency name", blank=True)
    symbol = models.CharField(max_length=5, help_text="Currency symbol (e.g., $, €, £)")
    is_active = models.BooleanField(default=True, help_text="Whether this currency is available for use")
    is_default = models.BooleanField(default=False, help_text="Whether this is the default currency")
    is_popular = models.BooleanField(default=False, help_text="Whether this is a popular currency")
    exchange_rate = models.DecimalField(max_digits=15, decimal_places=6, default=1.000000, 
                                       help_text="Exchange rate relative to base currency")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'currency'
        verbose_name = 'Currency'
        verbose_name_plural = 'Currencies'
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.name}"

    def save(self, *args, **kwargs):
        # Ensure only one default currency exists
        if self.is_default:
            Currency.objects.filter(is_default=True).update(is_default=False)
        self.full_clean()
        super().save(*args, **kwargs)

    @classmethod
    def get_default_currency(cls):
        """Get the default currency"""
        return cls.objects.filter(is_default=True).first()

    @classmethod
    def get_active_currencies(cls):
        """Get all active currencies"""
        return cls.objects.filter(is_active=True)


class Province(models.Model):
    """
    Afghanistan Provinces
    """
    name = models.CharField(max_length=64, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'province'
        verbose_name = 'Province'
        verbose_name_plural = 'Provinces'
        ordering = ['name']

    def __str__(self):
        return self.name


class Service(models.Model):
    """Service owned by a specific Saraf"""
    saraf = models.ForeignKey('SarafProfile', on_delete=models.CASCADE, related_name='services', null=True, blank=True)
    title = models.CharField(max_length=128)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'service'
        verbose_name = 'Service'
        verbose_name_plural = 'Services'
        unique_together = ('saraf', 'title')
        ordering = ['saraf_id', 'title']

    def __str__(self):
        return self.title

class SupportedCurrency(models.Model):
    """
    Model to track which currencies are supported by each saraf
    """
    saraf = models.ForeignKey('SarafProfile', on_delete=models.CASCADE, related_name='supported_currencies')
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name='supporting_sarafs')
    is_active = models.BooleanField(default=True)
    custom_rate = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True,
                                     help_text="Custom exchange rate for this saraf")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'supported_currency'
        verbose_name = 'Supported Currency'
        verbose_name_plural = 'Supported Currencies'
        unique_together = ['saraf', 'currency']

    def __str__(self):
        return f"{self.saraf.name} - {self.currency.code}"

    def get_effective_rate(self):
        """Get the effective exchange rate (custom or default)"""
        return self.custom_rate if self.custom_rate else self.currency.exchange_rate


class PasswordReset(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reset_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_when = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Password reset for {self.user.username} at {self.created_when}"


class sendhawala(models.Model):

    STATUS_CHOICES = [
        ('finished', 'Finished'),
        ('started', 'Started'),
        ('snoozed', 'Snoozed'),
    ]

    send_hawala_id = models.AutoField(primary_key=True)
    hawala_number = models.IntegerField(unique=True)
    sender_name = models.CharField(max_length=32)
    receiver_name = models.CharField(max_length=32)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT, null=True, blank=True)
    receiver_location = models.CharField(max_length=64)
    exchanger_location = models.CharField(max_length=64)
    sender_phone = models.CharField(
        max_length=15,
        validators=[RegexValidator(r'^0\d{9}$', 'Phone must be 10 digits and start with 0')]
    )
    hawala_fee = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    hawala_fee_currency = models.ForeignKey(Currency, on_delete=models.PROTECT, 
                                           related_name='hawala_fees', 
                                           null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='finished')

    def save(self, *args, **kwargs):
        # Auto-generate hawala_number if not provided
        if not self.hawala_number:
            # Get the highest hawala_number and increment by 1
            last_hawala = sendhawala.objects.aggregate(models.Max('hawala_number'))['hawala_number__max']
            self.hawala_number = (last_hawala or 0) + 1
        
        # Set default currency if not provided
        if not self.currency_id:
            default_currency = Currency.get_default_currency()
            if default_currency:
                self.currency = default_currency
        
        # Set default fee currency if not provided
        if not self.hawala_fee_currency_id:
            default_currency = Currency.get_default_currency()
            if default_currency:
                self.hawala_fee_currency = default_currency
        
        self.full_clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Hawala #{self.hawala_number} - {self.sender_name} to {self.receiver_name}"

    def get_amount_in_default_currency(self):
        """Convert amount to default currency"""
        default_currency = Currency.get_default_currency()
        if not self.currency:
            return self.amount
        if self.currency == default_currency:
            return self.amount
        return self.amount * self.currency.exchange_rate

    def get_fee_in_default_currency(self):
        """Convert fee to default currency"""
        if not self.hawala_fee:
            return 0
        default_currency = Currency.get_default_currency()
        if not self.hawala_fee_currency:
            return self.hawala_fee
        if self.hawala_fee_currency == default_currency:
            return self.hawala_fee
        return self.hawala_fee * self.hawala_fee_currency.exchange_rate


class ReceiveHawala(models.Model):
    """Model to track receiver verification for hawala transactions with complete sendhawala data"""
    # Reference to original sendhawala (optional for tracking)
    sendhawala = models.OneToOneField(
        'sendhawala',
        on_delete=models.CASCADE,
        related_name='receive_hawala'
    )
    
    # Copy all sendhawala fields for complete record
    hawala_number = models.CharField(max_length=20, default='', help_text="Hawala transaction number")
    sender_name = models.CharField(max_length=100, default='', help_text="Name of the sender")
    receiver_name = models.CharField(max_length=100, default='', help_text="Name of the receiver")
    amount = models.DecimalField(max_digits=15, decimal_places=2, default=0, help_text="Transaction amount")
    currency = models.ForeignKey('Currency', on_delete=models.PROTECT, null=True, help_text="Transaction currency")
    receiver_location = models.ForeignKey(
        'Province',
        on_delete=models.PROTECT,
        related_name='receive_hawala_receiver_location',
        null=True,
        help_text="Receiver's location"
    )
    exchanger_location = models.ForeignKey(
        'Province',
        on_delete=models.PROTECT,
        related_name='receive_hawala_exchanger_location',
        null=True,
        help_text="Exchanger's location"
    )
    sender_phone = models.CharField(max_length=15, default='', help_text="Sender's phone number")
    hawala_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Transaction fee")
    hawala_fee_currency = models.ForeignKey(
        'Currency',
        on_delete=models.PROTECT,
        related_name='receive_hawala_fee_currency',
        null=True,
        help_text="Currency for the transaction fee"
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('draft', 'Draft'),
            ('started', 'Started'),
            ('snoozed', 'Snoozed'),
        ],
        default='draft',
        help_text="Transaction status"
    )
    dates = models.DateTimeField(null=True, help_text="Transaction date")
    
    # Additional receiver verification fields
    receiver_phone = models.CharField(max_length=15, help_text="Receiver's phone number")
    receiver_id_card_photo = models.ImageField(
        upload_to='receiver_photos/',
        null=True,
        blank=True,
        help_text="Photo of receiver's ID card"
    )
    receiver_finger_photo = models.ImageField(
        upload_to='receiver_photos/',
        null=True,
        blank=True,
        help_text="Photo of receiver's fingerprint"
    )
    receiver_address = models.TextField(help_text="Receiver's physical address")
    
    # Tracking fields
    created_at = models.DateTimeField(auto_now_add=True)
    verified_by = models.ForeignKey(
        'SarafProfile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Saraf who verified the receiver"
    )
    verification_date = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'core_receive_hawala'
        verbose_name = 'Receive Hawala'
        verbose_name_plural = 'Receive Hawalas'
    
    def __str__(self):
        return f"Receive Hawala #{self.hawala_number} - {self.receiver_name}"


class CustomerAccount(models.Model):
    """Customer accounts managed by Saraf profiles"""
    # Mandatory fields
    account_number = models.CharField(
        max_length=20,
        unique=True,
        help_text="Unique customer account number"
    )
    full_name = models.CharField(max_length=100, help_text="Customer's full name")
    
    # Relationship to Saraf
    saraf = models.ForeignKey(
        'SarafProfile',
        on_delete=models.CASCADE,
        related_name='customer_accounts',
        help_text="Saraf who manages this customer account"
    )
    
    # Optional fields
    phone = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        validators=[RegexValidator(r'^0\d{9}$', 'Phone must be 10 digits and start with 0')],
        help_text="Customer's phone number"
    )
    address = models.TextField(blank=True, null=True, help_text="Customer's address")
    job = models.CharField(max_length=100, blank=True, null=True, help_text="Customer's job/occupation")
    finger_photo = models.ImageField(
        upload_to='customer_photos/',
        blank=True,
        null=True,
        help_text="Customer's fingerprint photo"
    )
    photo = models.ImageField(
        upload_to='customer_photos/',
        blank=True,
        null=True,
        help_text="Customer's photo"
    )
    
    # Balance field
    balance = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        help_text="Customer's current balance"
    )
    
    # Tracking fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'customer_account'
        verbose_name = 'Customer Account'
        verbose_name_plural = 'Customer Accounts'
        unique_together = ['saraf', 'account_number']
    
    def __str__(self):
        return f"{self.account_number} - {self.full_name} ({self.saraf.exchange_name})"
    
    def get_balances(self):
        """Get all currency balances for this customer"""
        return CustomerBalance.objects.filter(customer=self, is_active=True)
    
    def get_balance_for_currency(self, currency):
        """Get balance for a specific currency"""
        try:
            balance = CustomerBalance.objects.get(customer=self, currency=currency)
            return balance.balance
        except CustomerBalance.DoesNotExist:
            return 0
    
    def update_main_balance(self):
        """Update the main balance field with USD equivalent or primary currency balance"""
        from decimal import Decimal
        
        # Try to get USD balance first (primary currency)
        try:
            usd_currency = Currency.objects.get(code='USD')
            usd_balance = self.get_balance_for_currency(usd_currency)
            self.balance = usd_balance
        except Currency.DoesNotExist:
            # If USD doesn't exist, use the first available currency balance
            customer_balances = CustomerBalance.objects.filter(customer=self, is_active=True)
            if customer_balances.exists():
                self.balance = customer_balances.first().balance
            else:
                self.balance = Decimal('0')
        
        self.save(update_fields=['balance'])
    
    
    def deposit(self, currency, amount, description=""):
        """Customer deposits money"""
        from decimal import Decimal
        
        # Get or create customer balance
        customer_balance, created = CustomerBalance.objects.get_or_create(
            customer=self,
            currency=currency,
            defaults={'balance': Decimal('0')}
        )
        
        # Update balance
        customer_balance.balance += amount
        customer_balance.save()
        
        # Create transaction record
        CustomerTransaction.objects.create(
            customer=self,
            transaction_type='deposit',
            currency=currency,
            amount=amount,
            description=description,
            balance_after=customer_balance.balance
        )
        
        # Update main balance field
        self.update_main_balance()
        
        return customer_balance.balance
    
    def withdraw(self, currency, amount, description=""):
        """Customer withdraws money"""
        customer_balance = CustomerBalance.objects.get(customer=self, currency=currency)
        
        if customer_balance.balance < amount:
            raise ValueError("Insufficient balance for withdrawal")
        
        # Update balance
        customer_balance.balance -= amount
        customer_balance.save()
        
        # Create transaction record
        CustomerTransaction.objects.create(
            customer=self,
            transaction_type='withdrawal',
            currency=currency,
            amount=amount,
            description=description,
            balance_after=customer_balance.balance
        )
        
        # Update main balance field
        self.update_main_balance()
        
        return customer_balance.balance


class CustomerBalance(models.Model):
    """Customer balance for different currencies"""
    customer = models.ForeignKey(CustomerAccount, on_delete=models.CASCADE, related_name='balances')
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'customer_balance'
        unique_together = ['customer', 'currency']
        verbose_name = 'Customer Balance'
        verbose_name_plural = 'Customer Balances'
    
    def __str__(self):
        return f"{self.customer.full_name} - {self.currency.name}: {self.balance}"


class CustomerTransaction(models.Model):
    """Transaction history for customer accounts"""
    TRANSACTION_TYPES = [
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
    ]
    
    customer = models.ForeignKey(CustomerAccount, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    balance_after = models.DecimalField(max_digits=15, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'customer_transaction'
        verbose_name = 'Customer Transaction'
        verbose_name_plural = 'Customer Transactions'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.customer.full_name} - {self.transaction_type}: {self.amount} {self.currency.code}"


class Message(models.Model):
    """Messages between users (SarafProfile and NormalUserProfile)"""
    MESSAGE_TYPES = [
        ('text', 'Text'),
        ('attachment', 'Attachment'),
        ('mixed', 'Text with Attachment'),
    ]
    
    # Generic foreign key approach to handle both user types
    sender_saraf = models.ForeignKey(
        'SarafProfile', 
        on_delete=models.CASCADE, 
        related_name='sent_messages',
        null=True, 
        blank=True
    )
    sender_normal_user = models.ForeignKey(
        'normal_user_Profile', 
        on_delete=models.CASCADE, 
        related_name='sent_messages',
        null=True, 
        blank=True
    )
    
    receiver_saraf = models.ForeignKey(
        'SarafProfile', 
        on_delete=models.CASCADE, 
        related_name='received_messages',
        null=True, 
        blank=True
    )
    receiver_normal_user = models.ForeignKey(
        'normal_user_Profile', 
        on_delete=models.CASCADE, 
        related_name='received_messages',
        null=True, 
        blank=True
    )
    
    # Message content
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES, default='text')
    content = models.TextField(blank=True, null=True, help_text="Text content of the message")
    
    # Message status
    is_read = models.BooleanField(default=False)
    is_deleted_by_sender = models.BooleanField(default=False)
    is_deleted_by_receiver = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'message'
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'
        ordering = ['-created_at']
    
    def clean(self):
        from django.core.exceptions import ValidationError
        # Ensure exactly one sender and one receiver
        senders = sum([bool(self.sender_saraf), bool(self.sender_normal_user)])
        receivers = sum([bool(self.receiver_saraf), bool(self.receiver_normal_user)])
        
        if senders != 1:
            raise ValidationError("Message must have exactly one sender")
        if receivers != 1:
            raise ValidationError("Message must have exactly one receiver")
        
        # Prevent self-messaging
        if (self.sender_saraf and self.receiver_saraf and self.sender_saraf == self.receiver_saraf) or \
           (self.sender_normal_user and self.receiver_normal_user and self.sender_normal_user == self.receiver_normal_user):
            raise ValidationError("Cannot send message to yourself")
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    @property
    def sender_name(self):
        if self.sender_saraf:
            return self.sender_saraf.exchange_name
        elif self.sender_normal_user:
            return self.sender_normal_user.full_name
        return "Unknown"
    
    @property
    def receiver_name(self):
        if self.receiver_saraf:
            return self.receiver_saraf.exchange_name
        elif self.receiver_normal_user:
            return self.receiver_normal_user.full_name
        return "Unknown"
    
    def __str__(self):
        return f"{self.sender_name} → {self.receiver_name}: {self.content[:50] if self.content else 'Attachment'}..."


class MessageAttachment(models.Model):
    """File attachments for messages (photos, videos, documents)"""
    ATTACHMENT_TYPES = [
        ('image', 'Image'),
        ('video', 'Video'),
        ('document', 'Document'),
        ('audio', 'Audio'),
    ]
    
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='attachments')
    attachment_type = models.CharField(max_length=20, choices=ATTACHMENT_TYPES)
    file = models.FileField(upload_to='message_attachments/%Y/%m/%d/')
    file_name = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField(help_text="File size in bytes")
    mime_type = models.CharField(max_length=100, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'message_attachment'
        verbose_name = 'Message Attachment'
        verbose_name_plural = 'Message Attachments'
    
    def save(self, *args, **kwargs):
        if self.file:
            self.file_name = self.file.name
            self.file_size = self.file.size
            
            # Determine attachment type based on file extension
            file_extension = self.file.name.lower().split('.')[-1]
            if file_extension in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']:
                self.attachment_type = 'image'
            elif file_extension in ['mp4', 'avi', 'mov', 'wmv', 'flv', 'webm']:
                self.attachment_type = 'video'
            elif file_extension in ['mp3', 'wav', 'ogg', 'aac', 'm4a']:
                self.attachment_type = 'audio'
            else:
                self.attachment_type = 'document'
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.message.sender_name} - {self.attachment_type}: {self.file_name}"


class SarafProfile(models.Model):
    saraf_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=32)
    last_name = models.CharField(max_length=32)
    phone = models.CharField(
        max_length=15,
        unique=True,
        validators=[RegexValidator(r'^0\d{9}$', 'Phone must be 10 digits and start with 0')]
    )
    email = models.CharField(max_length=128, unique=True)
    password_hash = models.CharField(max_length=255, editable=False)  # Store hashed password only
    license_no = models.CharField(max_length=64, unique=True)
    exchange_name = models.CharField(max_length=128, null=True, blank=True, help_text="Registered exchange business name")
    saraf_address = models.CharField(max_length=255)
    provinces = models.ManyToManyField('Province', blank=True, related_name='sarafs')
    about_us = models.TextField(null=True, blank=True)
    work_history = models.IntegerField(null=True, blank=True)
    # Remove the old support_currencies field as we now use the SupportedCurrency model
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    saraf_logo = models.ImageField(upload_to='saraf_photos/', null=True, blank=True)
    saraf_logo_wallpeper = models.ImageField(upload_to='saraf_photos/', null=True, blank=True)
    licence_photo = models.ImageField(upload_to='saraf_photos/', null=True, blank=True)
    
    class Meta:
        db_table = 'saraf_profile'
        verbose_name = 'Saraf Profile'
        verbose_name_plural = 'Saraf Profiles'
    
    def __str__(self):
        return f"{self.name} {self.last_name} - {self.license_no}"

    def get_supported_currencies(self):
        """Get all currencies supported by this saraf"""
        return Currency.objects.filter(
            supporting_sarafs__saraf=self,
            supporting_sarafs__is_active=True
        )

    def add_supported_currency(self, currency, custom_rate=None):
        """Add a supported currency for this saraf"""
        SupportedCurrency.objects.get_or_create(
            saraf=self,
            currency=currency,
            defaults={'custom_rate': custom_rate}
        )

    def remove_supported_currency(self, currency):
        """Remove a supported currency for this saraf"""
        SupportedCurrency.objects.filter(saraf=self, currency=currency).delete()

    def set_password(self, raw_password):
        """
        Securely hash and store the password
        """
        if not self._validate_password(raw_password):
            raise ValidationError("Password does not meet security requirements")
        
        self.password_hash = make_password(raw_password)
        # Only save if object already exists in database
        if self.pk:
            self.save(update_fields=['password_hash'])

    def check_password(self, raw_password):
        """
        Verify if the provided password matches the stored hash
        """
        return check_password(raw_password, self.password_hash)

    def _validate_password(self, password):
        """
        Validate password strength
        """
        if len(password) < 6:
            return False
        
        # Check for at least one uppercase letter
        if not re.search(r'[A-Z]', password):
            return False
        
        # Check for at least one lowercase letter
        if not re.search(r'[a-z]', password):
            return False
        
        # Check for at least one digit
        if not re.search(r'\d', password):
            return False
        
        # Check for at least one special character
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False
        
        return True

    def get_password_requirements(self):
        """
        Return password requirements for user guidance
        """
        return {
            'min_length': 6,
            'requires_uppercase': True,
            'requires_lowercase': True,
            'requires_digit': True,
            'requires_special': True,
            'requirements': [
                'At least 6 characters long',
                'At least one uppercase letter (A-Z)',
                'At least one lowercase letter (a-z)',
                'At least one digit (0-9)',
                'At least one special character (!@#$%^&*(),.?":{}|<>)'
            ]
        }

    def save(self, *args, **kwargs):
        """
        Override save to ensure password is never stored in plain text
        """
        # Remove any plain text password field if it exists
        if hasattr(self, 'password'):
            delattr(self, 'password')
        
        self.full_clean()
        super().save(*args, **kwargs)




class SarafPost(models.Model):
    """Posts created by Saraf users"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
    ]

    saraf = models.ForeignKey('SarafProfile', on_delete=models.CASCADE, related_name='posts')
    title = models.CharField(max_length=150)
    content = models.TextField(blank=True)
    image = models.ImageField(upload_to='saraf_photos/', null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='published')
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'saraf_post'
        verbose_name = 'Saraf Post'
        verbose_name_plural = 'Saraf Posts'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.saraf.exchange_name or self.saraf.name}: {self.title}"

    def clean(self):
        if not self.title or not self.title.strip():
            raise ValidationError({'title': 'Title is required'})
        if not (self.content and self.content.strip()) and not self.image:
            raise ValidationError({'content': 'Provide content or an image'})


class SarafColleague(models.Model):
    """
    Model to manage colleague relationships between sarafs.
    Allows sarafs to add other sarafs as colleagues directly without acceptance.
    """
    COLLEAGUE_STATUS_CHOICES = [
        ('delivered', 'Delivered'),
        ('undelivered', 'Undelivered'),
    ]
    
    requester = models.ForeignKey('SarafProfile', on_delete=models.CASCADE, related_name='colleague_requests_sent')
    colleague = models.ForeignKey('SarafProfile', on_delete=models.CASCADE, related_name='colleague_requests_received')
    status = models.CharField(
        max_length=15,
        choices=COLLEAGUE_STATUS_CHOICES,
        default='undelivered',
        help_text="Status of the colleague relationship"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['requester', 'colleague']
        verbose_name = 'Saraf Colleague'
        verbose_name_plural = 'Saraf Colleagues'
    
    def clean(self):
        """Validate that saraf cannot add themselves as colleague"""
        if self.requester == self.colleague:
            raise ValidationError("Cannot add yourself as a colleague")
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.requester.exchange_name} -> {self.colleague.exchange_name}"
    


class SarafLoan(models.Model):
    """
    Simplified model to track loans between sarfs.
    """
    LOAN_STATUS_CHOICES = [
        ('delivered', 'Delivered'),
        ('undelivered', 'Undelivered'),
    ]
    
    lender = models.ForeignKey(
        'SarafProfile',
        on_delete=models.CASCADE,
        related_name='loans_given',
        help_text="Saraf who gave the loan"
    )
    borrower = models.ForeignKey(
        'SarafProfile',
        on_delete=models.CASCADE,
        related_name='loans_received',
        help_text="Saraf who received the loan"
    )
    currency = models.ForeignKey(
        'Currency',
        on_delete=models.PROTECT,
        help_text="Currency of the loan"
    )
    amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        help_text="Loan amount"
    )
    status = models.CharField(
        max_length=15,
        choices=LOAN_STATUS_CHOICES,
        default='undelivered',
        help_text="Delivery status of the loan"
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Additional notes about the loan"
    )
    date = models.DateTimeField(
        auto_now_add=True,
        help_text="Date of the loan"
    )
    
    class Meta:
        db_table = 'saraf_loan'
        verbose_name = 'Saraf Loan'
        verbose_name_plural = 'Saraf Loans'
        ordering = ['-date']
    
    def clean(self):
        """Validate loan constraints"""
        if self.lender == self.borrower:
            raise ValidationError("A saraf cannot give a loan to themselves")
        
        if self.amount <= 0:
            raise ValidationError("Loan amount must be greater than zero")
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.lender.exchange_name} -> {self.borrower.exchange_name}: {self.amount} {self.currency.code}"


class CurrencyExchange(models.Model):
    """
    Model to track currency exchanges between sarfs.
    """
    EXCHANGE_STATUS_CHOICES = [
        ('delivered', 'Delivered'),
        ('undelivered', 'Undelivered'),
    ]
    
    exchanger = models.ForeignKey(
        'SarafProfile',
        on_delete=models.CASCADE,
        related_name='exchanges_made',
        help_text="Saraf who initiated the exchange"
    )
    receiver = models.ForeignKey(
        'SarafProfile',
        on_delete=models.CASCADE,
        related_name='exchanges_received',
        help_text="Saraf who received the exchange"
    )
    from_currency = models.ForeignKey(
        'Currency',
        on_delete=models.PROTECT,
        related_name='exchanges_from',
        help_text="Currency being exchanged from"
    )
    to_currency = models.ForeignKey(
        'Currency',
        on_delete=models.PROTECT,
        related_name='exchanges_to',
        help_text="Currency being exchanged to"
    )
    amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        help_text="Amount in from_currency"
    )
    rate = models.DecimalField(
        max_digits=10,
        decimal_places=6,
        help_text="Exchange rate (to_currency per from_currency)"
    )
    status = models.CharField(
        max_length=15,
        choices=EXCHANGE_STATUS_CHOICES,
        default='undelivered',
        help_text="Delivery status of the exchange"
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Additional notes about the exchange"
    )
    date = models.DateTimeField(
        auto_now_add=True,
        help_text="Date of the exchange"
    )
    
    class Meta:
        db_table = 'currency_exchange'
        verbose_name = 'Currency Exchange'
        verbose_name_plural = 'Currency Exchanges'
        ordering = ['-date']
    
    def clean(self):
        """Validate exchange constraints"""
        if self.exchanger == self.receiver:
            raise ValidationError("A saraf cannot exchange with themselves")
        
        if self.amount <= 0:
            raise ValidationError("Exchange amount must be greater than zero")
        
        if self.rate <= 0:
            raise ValidationError("Exchange rate must be greater than zero")
        
        if self.from_currency == self.to_currency:
            raise ValidationError("Cannot exchange the same currency")
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.exchanger.exchange_name} -> {self.receiver.exchange_name}: {self.amount} {self.from_currency.code} to {self.to_currency.code}"
    
    def calculate_converted_amount(self):
        """Calculate the amount in to_currency"""
        return self.amount * self.rate


class normal_user_Profile(models.Model):
    normal_user_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=32)
    last_name = models.CharField(max_length=32)
    phone = models.CharField(
        max_length=15,
        unique=True,
        validators=[RegexValidator(r'^0\d{9}$', 'Phone must be 10 digits and start with 0')]
    )
    email = models.CharField(max_length=128, unique=True)
    password_hash = models.CharField(max_length=255, editable=False)  # Store hashed password only
    preferred_currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True, blank=True,
                                          help_text="User's preferred currency for transactions")
    user_logo = models.ImageField(upload_to='normal_user_photos/', null=True, blank=True, 
                                 help_text="User's profile logo/avatar")
    user_wallpaper = models.ImageField(upload_to='normal_user_photos/', null=True, blank=True,
                                      help_text="User's profile wallpaper/background image")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'normal_user_profile'
        verbose_name = 'Normal User Profile'
        verbose_name_plural = 'Normal User Profiles'

    @property
    def full_name(self):
        """Return full name combining first and last name"""
        return f"{self.name} {self.last_name}".strip()

    def __str__(self):
        return f"{self.name} {self.last_name} - {self.phone}"

    def get_preferred_currency(self):
        """Get user's preferred currency or default currency"""
        return self.preferred_currency or Currency.get_default_currency()

    def set_password(self, raw_password):
        """
        Securely hash and store the password
        """
        if not self._validate_password(raw_password):
            raise ValidationError("Password does not meet security requirements")
        
        self.password_hash = make_password(raw_password)
        # Only save if object already exists in database
        if self.pk:
            self.save(update_fields=['password_hash'])

    def check_password(self, raw_password):
        """
        Verify if the provided password matches the stored hash
        """
        return check_password(raw_password, self.password_hash)

    def _validate_password(self, password):
        """
        Validate password strength
        """
        if len(password) < 6:
            return False
        
        # Check for at least one uppercase letter
        if not re.search(r'[A-Z]', password):
            return False
        
        # Check for at least one lowercase letter
        if not re.search(r'[a-z]', password):
            return False
        
        # Check for at least one digit
        if not re.search(r'\d', password):
            return False
        
        # Check for at least one special character
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False
        
        return True

    def get_password_requirements(self):
        """
        Return password requirements for user guidance
        """
        return {
            'min_length': 6,
            'requires_uppercase': True,
            'requires_lowercase': True,
            'requires_digit': True,
            'requires_special': True,
            'requirements': [
                'At least 6 characters long',
                'At least one uppercase letter (A-Z)',
                'At least one lowercase letter (a-z)',
                'At least one digit (0-9)',
                'At least one special character (!@#$%^&*(),.?":{}|<>)'
            ]
        }

    def save(self, *args, **kwargs):
        """
        Override save to ensure password is never stored in plain text
        """
        # Remove any plain text password field if it exists
        if hasattr(self, 'password'):
            delattr(self, 'password')
        
        self.full_clean()
        super().save(*args, **kwargs)