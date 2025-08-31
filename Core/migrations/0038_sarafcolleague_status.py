# Generated migration for adding status field to SarafColleague

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Core', '0037_auto_20250825_2344'),
    ]

    operations = [
        migrations.AddField(
            model_name='sarafcolleague',
            name='status',
            field=models.CharField(
                choices=[('delivered', 'Delivered'), ('undelivered', 'Undelivered')],
                default='undelivered',
                help_text='Status of the colleague relationship',
                max_length=15
            ),
        ),
    ]
