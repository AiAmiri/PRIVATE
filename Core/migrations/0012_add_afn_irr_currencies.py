from django.db import migrations

AFN = {
    'code': 'AFN',
    'name': 'Afghan Afghani',
    'symbol': '؋',
    'is_active': True,
}
IRR = {
    'code': 'IRR',
    'name': 'Iranian Rial',
    'symbol': '﷼',
    'is_active': True,
}

def add_currencies(apps, schema_editor):
    Currency = apps.get_model('Core', 'Currency')
    for data in (AFN, IRR):
        obj, created = Currency.objects.get_or_create(code=data['code'], defaults=data)
        # If it exists but was inactive, activate it
        if not created and obj.is_active is False:
            obj.is_active = True
            obj.save(update_fields=['is_active'])


def remove_currencies(apps, schema_editor):
    Currency = apps.get_model('Core', 'Currency')
    Currency.objects.filter(code__in=['AFN', 'IRR']).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('Core', '0011_update_sarafphoto_fields'),
    ]

    operations = [
        migrations.RunPython(add_currencies, remove_currencies),
    ]
