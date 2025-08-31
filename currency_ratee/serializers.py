from rest_framework import serializers
from .models import CurrencyRate


class CurrencyRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CurrencyRate
        fields = [
            'currency_code',
            'rate',
            'base_currency',
            'bank_name',
            'country_code',
            'date_fetched'
        ]
        read_only_fields = ['date_fetched']
