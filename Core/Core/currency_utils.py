from decimal import Decimal
from .models import Currency, SupportedCurrency

def convert_currency(amount, from_currency, to_currency):
    """
    Convert amount from one currency to another
    """
    if from_currency == to_currency:
        return amount
    
    # Convert to default currency first, then to target currency
    default_currency = Currency.get_default_currency()
    
    if from_currency == default_currency:
        # Direct conversion from default currency
        return amount * to_currency.exchange_rate
    elif to_currency == default_currency:
        # Direct conversion to default currency
        return amount / from_currency.exchange_rate
    else:
        # Convert through default currency
        amount_in_default = amount / from_currency.exchange_rate
        return amount_in_default * to_currency.exchange_rate

def format_currency_amount(amount, currency):
    """
    Format amount with currency symbol
    """
    if currency:
        return f"{currency.symbol}{amount:,.2f}"
    return f"{amount:,.2f}"

def get_currency_choices():
    """
    Get currency choices for forms
    """
    currencies = Currency.get_active_currencies()
    return [(currency.id, f"{currency.code} - {currency.name}") for currency in currencies]

def get_saraf_supported_currencies(saraf):
    """
    Get currencies supported by a specific saraf
    """
    return Currency.objects.filter(
        supporting_sarafs__saraf=saraf,
        supporting_sarafs__is_active=True
    )

def update_exchange_rates():
    """
    Update exchange rates (this would typically call an external API)
    Placeholder for future implementation
    """
    # This would typically call an external API like:
    # - Exchange Rate API
    # - Fixer.io
    # - Currency Layer
    # - Open Exchange Rates
    pass

def get_currency_by_code(code):
    """
    Get currency by ISO code
    """
    try:
        return Currency.objects.get(code=code.upper(), is_active=True)
    except Currency.DoesNotExist:
        return None

def get_default_currency():
    """
    Get the default currency
    """
    return Currency.get_default_currency()

def set_default_currency(currency):
    """
    Set a new default currency
    """
    if currency.is_active:
        # Remove current default
        Currency.objects.filter(is_default=True).update(is_default=False)
        # Set new default
        currency.is_default = True
        currency.save()
        return True
    return False
