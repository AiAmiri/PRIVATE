from django.core.management.base import BaseCommand, CommandError
from Core.models import Currency, SupportedCurrency, SarafProfile
from decimal import Decimal

class Command(BaseCommand):
    help = 'Manage currencies in the system'

    def add_arguments(self, parser):
        parser.add_argument(
            'action',
            choices=['list', 'add', 'update', 'set-default', 'deactivate', 'activate'],
            help='Action to perform'
        )
        parser.add_argument(
            '--code',
            type=str,
            help='Currency code (e.g., USD, EUR)'
        )
        parser.add_argument(
            '--name',
            type=str,
            help='Currency name'
        )
        parser.add_argument(
            '--symbol',
            type=str,
            help='Currency symbol'
        )
        parser.add_argument(
            '--rate',
            type=float,
            help='Exchange rate'
        )

    def handle(self, *args, **options):
        action = options['action']

        if action == 'list':
            self.list_currencies()
        elif action == 'add':
            self.add_currency(options)
        elif action == 'update':
            self.update_currency(options)
        elif action == 'set-default':
            self.set_default_currency(options)
        elif action == 'deactivate':
            self.deactivate_currency(options)
        elif action == 'activate':
            self.activate_currency(options)

    def list_currencies(self):
        currencies = Currency.objects.all().order_by('code')
        self.stdout.write(
            self.style.SUCCESS(f'Found {currencies.count()} currencies:')
        )
        
        for currency in currencies:
            status = 'DEFAULT' if currency.is_default else 'ACTIVE' if currency.is_active else 'INACTIVE'
            self.stdout.write(
                f'{currency.code} - {currency.name} ({currency.symbol}) - {status} - Rate: {currency.exchange_rate}'
            )

    def add_currency(self, options):
        code = options.get('code')
        name = options.get('name')
        symbol = options.get('symbol')
        rate = options.get('rate')

        if not all([code, name, symbol, rate]):
            raise CommandError('All arguments (--code, --name, --symbol, --rate) are required for adding a currency')

        try:
            currency = Currency.objects.create(
                code=code.upper(),
                name=name,
                symbol=symbol,
                exchange_rate=Decimal(str(rate))
            )
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created currency: {currency.code} - {currency.name}')
            )
        except Exception as e:
            raise CommandError(f'Failed to create currency: {e}')

    def update_currency(self, options):
        code = options.get('code')
        if not code:
            raise CommandError('--code is required for updating a currency')

        try:
            currency = Currency.objects.get(code=code.upper())
            
            if options.get('name'):
                currency.name = options['name']
            if options.get('symbol'):
                currency.symbol = options['symbol']
            if options.get('rate'):
                currency.exchange_rate = Decimal(str(options['rate']))
            
            currency.save()
            self.stdout.write(
                self.style.SUCCESS(f'Successfully updated currency: {currency.code}')
            )
        except Currency.DoesNotExist:
            raise CommandError(f'Currency with code {code} not found')
        except Exception as e:
            raise CommandError(f'Failed to update currency: {e}')

    def set_default_currency(self, options):
        code = options.get('code')
        if not code:
            raise CommandError('--code is required for setting default currency')

        try:
            currency = Currency.objects.get(code=code.upper())
            if not currency.is_active:
                raise CommandError('Cannot set inactive currency as default')
            
            # Remove current default
            Currency.objects.filter(is_default=True).update(is_default=False)
            
            # Set new default
            currency.is_default = True
            currency.save()
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully set {currency.code} as default currency')
            )
        except Currency.DoesNotExist:
            raise CommandError(f'Currency with code {code} not found')
        except Exception as e:
            raise CommandError(f'Failed to set default currency: {e}')

    def deactivate_currency(self, options):
        code = options.get('code')
        if not code:
            raise CommandError('--code is required for deactivating a currency')

        try:
            currency = Currency.objects.get(code=code.upper())
            if currency.is_default:
                raise CommandError('Cannot deactivate default currency')
            
            currency.is_active = False
            currency.save()
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully deactivated currency: {currency.code}')
            )
        except Currency.DoesNotExist:
            raise CommandError(f'Currency with code {code} not found')
        except Exception as e:
            raise CommandError(f'Failed to deactivate currency: {e}')

    def activate_currency(self, options):
        code = options.get('code')
        if not code:
            raise CommandError('--code is required for activating a currency')

        try:
            currency = Currency.objects.get(code=code.upper())
            currency.is_active = True
            currency.save()
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully activated currency: {currency.code}')
            )
        except Currency.DoesNotExist:
            raise CommandError(f'Currency with code {code} not found')
        except Exception as e:
            raise CommandError(f'Failed to activate currency: {e}')
```

