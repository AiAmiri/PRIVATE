from celery import shared_task
import requests
from .models import CurrencyRate

@shared_task
def fetch_currency_rates():
    url = "https://api.bankfxapi.com/v1/bank/AFCB?api_key=43088180beddf039ac6bfde3e11d71453f5d6237"
    
    try:
        response = requests.get(url)
        data = response.json()

        if data.get("code") != 200:
            return "API error"

        meta = data.get("meta", {})
        rates = data.get("rates", {})

        for code, rate in rates.items():
            CurrencyRate.objects.create(
                currency_code=code,
                rate=rate,
                base_currency=meta.get("base_currency", "AFN"),
                bank_name=meta.get("bank_name", ""),
                country_code=meta.get("country_code", "")
            )

        return "Rates updated"

    except Exception as e:
        return f"Error: {str(e)}"
