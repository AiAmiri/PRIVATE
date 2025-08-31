import requests
from django.core.management.base import BaseCommand
from currency_ratee.models import CurrencyRate

class Command(BaseCommand):
    help = "Fetch currency exchange rates and save them to the database"

    def handle(self, *args, **kwargs):
        api_url = "https://api.bankfxapi.com/v1/bank/AFCB?api_key=43088180beddf039ac6bfde3e11d71453f5d6237"  # Replace with your actual API URL

        try:
            response = requests.get(api_url)
            data = response.json()

            if data.get("code") != 200:
                self.stdout.write(self.style.ERROR("API did not return success."))
                return

            rates = data.get("rates", {})
            meta = data.get("meta", {})

            for currency_code, rate in rates.items():
                CurrencyRate.objects.create(
                    currency_code=currency_code,
                    rate=rate,
                    base_currency=meta.get("base_currency", "AFN"),
                    bank_name=meta.get("bank_name", ""),
                    country_code=meta.get("country_code", "")
                )

            self.stdout.write(self.style.SUCCESS("Currency rates saved successfully."))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {str(e)}"))
