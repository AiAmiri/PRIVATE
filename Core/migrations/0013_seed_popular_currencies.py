from django.db import migrations


def seed_popular_currencies(apps, schema_editor):
    Currency = apps.get_model('Core', 'Currency')

    # Ensure AFN and IRR are active (added previously)
    for code, name, symbol in [
        ('AFN', 'Afghan Afghani', '؋'),
        ('IRR', 'Iranian Rial', '﷼'),
    ]:
        obj, created = Currency.objects.get_or_create(code=code, defaults={
            'name': name,
            'symbol': symbol,
            'is_active': True,
        })
        if not created:
            updated = False
            if not obj.is_active:
                obj.is_active = True
                updated = True
            # Backfill missing symbol/name if empty
            if not obj.symbol:
                obj.symbol = symbol
                updated = True
            if not obj.name:
                obj.name = name
                updated = True
            if updated:
                obj.save(update_fields=['is_active', 'symbol', 'name'])

    # Popular currencies used in Afghan exchanges
    # Note: Some currencies share the same symbol (e.g., SAR/QAR use ﷼). Use code to disambiguate.
    popular = [
        ('USD', 'US Dollar', '$'),
        ('PKR', 'Pakistani Rupee', '₨'),
        ('INR', 'Indian Rupee', '₹'),
        ('AED', 'UAE Dirham', 'د.إ'),
        ('EUR', 'Euro', '€'),
        ('TRY', 'Turkish Lira', '₺'),
        ('SAR', 'Saudi Riyal', '﷼'),
        ('QAR', 'Qatari Riyal', '﷼'),
        ('KWD', 'Kuwaiti Dinar', 'د.ك'),
        ('CNY', 'Chinese Yuan', '¥'),
    ]

    for code, name, symbol in popular:
        obj, created = Currency.objects.get_or_create(code=code, defaults={
            'name': name,
            'symbol': symbol,
            'is_active': True,
        })
        if not created:
            updated = False
            if not obj.is_active:
                obj.is_active = True
                updated = True
            if not obj.symbol:
                obj.symbol = symbol
                updated = True
            if not obj.name:
                obj.name = name
                updated = True
            if updated:
                obj.save(update_fields=['is_active', 'symbol', 'name'])


def unseed_popular_currencies(apps, schema_editor):
    # No-op on reverse to avoid deleting existing data in production
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('Core', '0012_add_afn_irr_currencies'),
    ]

    operations = [
        migrations.RunPython(seed_popular_currencies, unseed_popular_currencies),
    ]
