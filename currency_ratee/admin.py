from django.contrib import admin
from .models import CurrencyRate


@admin.register(CurrencyRate)
class CurrencyRateAdmin(admin.ModelAdmin):
    list_display = (
        "currency_code",
        "rate",
        "base_currency",
        "bank_name",
        "country_code",
        "date_fetched",
    )
    list_filter = ("bank_name", "base_currency", "country_code")
    search_fields = ("currency_code", "bank_name", "country_code")
    ordering = ("-date_fetched",)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
