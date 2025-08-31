from django.db import migrations


def seed_more_currencies(apps, schema_editor):
    Currency = apps.get_model('Core', 'Currency')
    extra = [
        ('GBP', 'British Pound', '£'),
        ('BHD', 'Bahraini Dinar', 'ب.د'),
        ('OMR', 'Omani Rial', 'ر.ع.'),
    ]
    for code, name, symbol in extra:
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


def unseed_more_currencies(apps, schema_editor):
    # No destructive reverse to avoid data loss
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('Core', '0013_seed_popular_currencies'),
    ]

    operations = [
        migrations.RunPython(seed_more_currencies, unseed_more_currencies),
    ]
