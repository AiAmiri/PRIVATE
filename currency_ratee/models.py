from django.db import models

class CurrencyRate(models.Model):
    currency_code = models.CharField(max_length=10)
    rate = models.DecimalField(max_digits=20, decimal_places=6)
    base_currency = models.CharField(max_length=10)
    bank_name = models.CharField(max_length=100)
    country_code = models.CharField(max_length=10)
    date_fetched = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.currency_code} - {self.rate}"
