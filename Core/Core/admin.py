from django.contrib import admin
from .models import (
    PasswordReset, 
    sendhawala, 
    ReceiveHawala,
    SarafProfile, 
    normal_user_Profile,
    Currency,
    SupportedCurrency,
    Province,
    Service,
    Message,
    MessageAttachment,
    SarafColleague,
    CustomerAccount,
    CustomerBalance,
    SarafPost,
)

@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'symbol', 'is_active', 'is_default', 'exchange_rate']
    list_filter = ['is_active', 'is_default']
    search_fields = ['code', 'name']
    ordering = ['code']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(SupportedCurrency)
class SupportedCurrencyAdmin(admin.ModelAdmin):
    list_display = ['saraf', 'currency', 'is_active', 'custom_rate', 'created_at']
    list_filter = ['is_active', 'currency']
    search_fields = ['saraf__name', 'saraf__last_name', 'currency__code', 'currency__name']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(PasswordReset)
class PasswordResetAdmin(admin.ModelAdmin):
    list_display = ['user', 'reset_id', 'created_when']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['reset_id', 'created_when']

@admin.register(sendhawala)
class sendhawalaAdmin(admin.ModelAdmin):
    list_display = ['send_hawala_id', 'hawala_number', 'sender_name', 'receiver_name', 
                   'amount', 'currency', 'status', 'created_at']
    list_filter = ['status', 'currency', 'created_at']
    search_fields = ['sender_name', 'receiver_name', 'hawala_number']
    readonly_fields = ['send_hawala_id', 'created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('hawala_number', 'sender_name', 'receiver_name', 'sender_phone')
        }),
        ('Transaction Details', {
            'fields': ('amount', 'currency', 'hawala_fee', 'hawala_fee_currency')
        }),
        ('Location', {
            'fields': ('receiver_location', 'exchanger_location')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Province)
class ProvinceAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']
    ordering = ['name']

class ServiceInline(admin.TabularInline):
    model = Service
    extra = 1
    fields = ('title', 'description', 'is_active')
    show_change_link = True

    can_delete = False

@admin.register(SarafProfile)
class SarafProfileAdmin(admin.ModelAdmin):
    list_display = ['saraf_id', 'name', 'last_name', 'phone', 'email', 'license_no', 'exchange_name', 'provinces_list', 'services_list', 'is_active']
    list_filter = ['is_active', 'created_at', 'provinces']
    search_fields = ['name', 'last_name', 'phone', 'email', 'license_no', 'exchange_name', 'provinces__name', 'services__title']
    readonly_fields = ['saraf_id', 'created_at', 'updated_at']
    filter_horizontal = ['provinces']
    inlines = [ServiceInline]
    fieldsets = (
        ('Personal Information', {
            'fields': ('name', 'last_name', 'phone', 'email')
        }),
        ('Business Information', {
            'fields': ('license_no', 'exchange_name', 'saraf_address', 'work_history')
        }),
        ('Coverage', {
            'fields': ('provinces',)
        }),
        ('Content', {
            'fields': ('about_us',)
        }),
        ('Status', {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
        ('Documents', {
            'fields': ('saraf_logo', 'saraf_logo_wallpeper', 'licence_photo'),
            'classes': ('collapse',)
        }),
    )

    def provinces_list(self, obj):
        return ", ".join(obj.provinces.values_list('name', flat=True))
    provinces_list.short_description = 'Provinces'

    def services_list(self, obj):
        return ", ".join(obj.services.values_list('title', flat=True))
    services_list.short_description = 'Services'


@admin.register(normal_user_Profile)
class normal_user_ProfileAdmin(admin.ModelAdmin):
    list_display = ['normal_user_id', 'name', 'last_name', 'phone', 'email', 'preferred_currency', 'has_logo', 'has_wallpaper']
    list_filter = ['created_at', 'preferred_currency']
    search_fields = ['name', 'last_name', 'phone', 'email']
    readonly_fields = ['normal_user_id', 'created_at', 'updated_at']
    fieldsets = (
        ('Personal Information', {
            'fields': ('name', 'last_name', 'phone', 'email')
        }),
        ('Preferences', {
            'fields': ('preferred_currency',)
        }),
        ('Profile Images', {
            'fields': ('user_logo', 'user_wallpaper'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_logo(self, obj):
        return bool(obj.user_logo)
    has_logo.boolean = True
    has_logo.short_description = 'Has Logo'
    
    def has_wallpaper(self, obj):
        return bool(obj.user_wallpaper)
    has_wallpaper.boolean = True
    has_wallpaper.short_description = 'Has Wallpaper'

# Message Admin
@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'get_sender', 'get_receiver', 'message_type', 'content_preview', 'is_read', 'created_at']
    list_filter = ['message_type', 'is_read', 'is_deleted_by_sender', 'is_deleted_by_receiver', 'created_at']
    search_fields = ['content', 'sender_saraf__name', 'sender_saraf__exchange_name', 
                    'sender_normal_user__name', 'receiver_saraf__name', 'receiver_saraf__exchange_name',
                    'receiver_normal_user__name']
    readonly_fields = ['created_at', 'read_at']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    fieldsets = (
        ('Message Content', {
            'fields': ('message_type', 'content')
        }),
        ('Sender Information', {
            'fields': ('sender_saraf', 'sender_normal_user')
        }),
        ('Receiver Information', {
            'fields': ('receiver_saraf', 'receiver_normal_user')
        }),
        ('Status', {
            'fields': ('is_read', 'read_at', 'is_deleted_by_sender', 'is_deleted_by_receiver')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_sender(self, obj):
        if obj.sender_saraf:
            return f"Saraf: {obj.sender_saraf.name} {obj.sender_saraf.last_name}"
        elif obj.sender_normal_user:
            return f"User: {obj.sender_normal_user.name} {obj.sender_normal_user.last_name}"
        return "Unknown"
    get_sender.short_description = 'Sender'
    
    def get_receiver(self, obj):
        if obj.receiver_saraf:
            return f"Saraf: {obj.receiver_saraf.name} {obj.receiver_saraf.last_name}"
        elif obj.receiver_normal_user:
            return f"User: {obj.receiver_normal_user.name} {obj.receiver_normal_user.last_name}"
        return "Unknown"
    get_receiver.short_description = 'Receiver'
    
    def content_preview(self, obj):
        if obj.content:
            return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
        return "No content"
    content_preview.short_description = 'Content Preview'

@admin.register(MessageAttachment)
class MessageAttachmentAdmin(admin.ModelAdmin):
    list_display = ['id', 'message', 'attachment_type', 'file_name', 'file_size', 'created_at']
    list_filter = ['attachment_type', 'created_at']
    search_fields = ['file_name', 'message__content']
    readonly_fields = ['created_at', 'file_size', 'file_name']
    date_hierarchy = 'created_at'

# Colleague Admin
@admin.register(SarafColleague)
class SarafColleagueAdmin(admin.ModelAdmin):
    list_display = ['id', 'get_requester', 'get_colleague', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['requester__name', 'requester__exchange_name', 'colleague__name', 'colleague__exchange_name']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    fieldsets = (
        ('Colleague Relationship', {
            'fields': ('requester', 'colleague', 'status')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_requester(self, obj):
        return f"{obj.requester.name} {obj.requester.last_name} ({obj.requester.exchange_name})"
    get_requester.short_description = 'Requester'
    
    def get_colleague(self, obj):
        return f"{obj.colleague.name} {obj.colleague.last_name} ({obj.colleague.exchange_name})"
    get_colleague.short_description = 'Colleague'

# SarafPost Admin
@admin.register(SarafPost)
class SarafPostAdmin(admin.ModelAdmin):
    list_display = ['id', 'get_saraf', 'title', 'status', 'is_featured', 'created_at']
    list_filter = ['status', 'is_featured', 'created_at']
    search_fields = ['title', 'content', 'saraf__name', 'saraf__exchange_name']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    fieldsets = (
        ('Post', {
            'fields': ('saraf', 'title', 'content', 'image')
        }),
        ('Visibility', {
            'fields': ('status', 'is_featured')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_saraf(self, obj):
        return f"{obj.saraf.name} {obj.saraf.last_name} ({obj.saraf.exchange_name})"
    get_saraf.short_description = 'Saraf'

# Customer Admin
class CustomerBalanceInline(admin.TabularInline):
    model = CustomerBalance
    extra = 0
    fields = ('currency', 'balance', 'updated_at')
    readonly_fields = ('balance', 'updated_at')
    can_delete = False

@admin.register(CustomerAccount)
class CustomerAccountAdmin(admin.ModelAdmin):
    list_display = ['id', 'account_number', 'full_name', 'get_saraf', 'phone', 'balance', 'is_active', 'created_at']
    list_filter = ['is_active', 'saraf', 'created_at']
    search_fields = ['account_number', 'full_name', 'phone', 'address', 'job', 'saraf__name', 'saraf__exchange_name']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    inlines = [CustomerBalanceInline]
    
    fieldsets = (
        ('Account Information', {
            'fields': ('account_number', 'full_name', 'saraf')
        }),
        ('Contact Information', {
            'fields': ('phone', 'address', 'job')
        }),
        ('Financial Information', {
            'fields': ('balance',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Documents', {
            'fields': ('finger_photo', 'photo'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_saraf(self, obj):
        return f"{obj.saraf.name} {obj.saraf.last_name} ({obj.saraf.exchange_name})"
    get_saraf.short_description = 'Saraf'

@admin.register(CustomerBalance)
class CustomerBalanceAdmin(admin.ModelAdmin):
    list_display = ['id', 'get_customer', 'currency', 'balance', 'updated_at']
    list_filter = ['currency', 'customer__saraf', 'updated_at']
    search_fields = ['customer__full_name', 'customer__account_number', 'currency__code']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'updated_at'
    ordering = ['-updated_at']
    
    def get_customer(self, obj):
        return f"{obj.customer.full_name} ({obj.customer.account_number})"
    get_customer.short_description = 'Customer'

@admin.register(ReceiveHawala)
class ReceiveHawalaAdmin(admin.ModelAdmin):
    list_display = ['id', 'hawala_number', 'sender_name', 'receiver_name', 'amount', 
                   'currency', 'receiver_phone', 'get_verified_by', 'verification_date', 'created_at']
    list_filter = ['currency', 'status', 'verified_by', 'verification_date', 'created_at']
    search_fields = ['hawala_number', 'sender_name', 'receiver_name', 'receiver_phone', 
                    'receiver_address', 'sendhawala__hawala_number']
    readonly_fields = ['id', 'hawala_number', 'sender_name', 'receiver_name', 
                      'amount', 'currency', 'sender_phone', 'hawala_fee', 'hawala_fee_currency',
                      'status', 'dates', 'created_at']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    fieldsets = (
        ('Required Information', {
            'fields': ('sendhawala',),
            'description': 'Select a SendHawala to automatically populate transaction details'
        }),
        ('Auto-populated Transaction Details', {
            'fields': ('hawala_number', 'sender_name', 'receiver_name', 'amount', 'currency', 'hawala_fee', 'hawala_fee_currency', 'status'),
            'classes': ('collapse',),
            'description': 'These fields are automatically filled from the selected SendHawala'
        }),
        ('Location Information', {
            'fields': ('receiver_location', 'exchanger_location'),
            'classes': ('collapse',)
        }),
        ('Receiver Verification', {
            'fields': ('receiver_phone', 'receiver_address', 'receiver_id_card_photo', 'receiver_finger_photo'),
            'description': 'Enter receiver verification details'
        }),
        ('Verification Status', {
            'fields': ('verified_by', 'verification_date')
        }),
        ('Timestamps', {
            'fields': ('dates', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_verified_by(self, obj):
        if obj.verified_by:
            return f"{obj.verified_by.name} {obj.verified_by.last_name} ({obj.verified_by.exchange_name})"
        return "Not verified"
    get_verified_by.short_description = 'Verified By'
    
    def get_form(self, request, obj=None, **kwargs):
        """Customize form for ReceiveHawala creation"""
        form = super().get_form(request, obj, **kwargs)
        if obj is None:  # Creating new object
            # Make sendhawala field required and filter to show only available ones
            form.base_fields['sendhawala'].queryset = sendhawala.objects.exclude(
                receive_hawala__isnull=False
            ).order_by('-created_at')
            form.base_fields['sendhawala'].empty_label = "Select SendHawala to link"
        return form
    
    def save_model(self, request, obj, form, change):
        """Auto-populate fields from linked sendhawala when creating"""
        if not change and obj.sendhawala:  # Creating new object with sendhawala
            send_hawala = obj.sendhawala
            
            # Copy sendhawala data
            obj.hawala_number = str(send_hawala.hawala_number)
            obj.sender_name = send_hawala.sender_name
            obj.receiver_name = send_hawala.receiver_name
            obj.amount = send_hawala.amount
            obj.currency = send_hawala.currency
            obj.sender_phone = send_hawala.sender_phone
            obj.hawala_fee = send_hawala.hawala_fee or 0
            obj.hawala_fee_currency = send_hawala.hawala_fee_currency
            obj.status = send_hawala.status
            obj.dates = send_hawala.created_at
            
            # Handle location fields
            if send_hawala.receiver_location:
                try:
                    receiver_location = Province.objects.get(
                        name__iexact=send_hawala.receiver_location, is_active=True
                    )
                    obj.receiver_location = receiver_location
                except Province.DoesNotExist:
                    pass
            
            if send_hawala.exchanger_location:
                try:
                    exchanger_location = Province.objects.get(
                        name__iexact=send_hawala.exchanger_location, is_active=True
                    )
                    obj.exchanger_location = exchanger_location
                except Province.DoesNotExist:
                    pass
        
        super().save_model(request, obj, form, change)