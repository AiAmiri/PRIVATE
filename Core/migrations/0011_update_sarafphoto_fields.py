from django.db import migrations, models


def copy_photo_fields(apps, schema_editor):
    SarafProfile = apps.get_model('Core', 'SarafProfile')
    for sp in SarafProfile.objects.all():
        # Copy old values to new fields if present
        try:
            if hasattr(sp, 'id_card_front_photo') and sp.id_card_front_photo:
                sp.saraf_logo = sp.id_card_front_photo
            if hasattr(sp, 'id_card_back_photo') and sp.id_card_back_photo:
                sp.saraf_logo_wallpeper = sp.id_card_back_photo
            if hasattr(sp, 'selfie_photo') and sp.selfie_photo:
                sp.licence_photo = sp.selfie_photo
            sp.save(update_fields=['saraf_logo', 'saraf_logo_wallpeper', 'licence_photo'])
        except Exception:
            # Best-effort copy; skip any problematic rows
            pass


def noop_reverse(apps, schema_editor):
    # No reverse data migration
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('Core', '0010_alter_sarafprofile_about_us_and_more'),
    ]

    operations = [
        # Add new fields first
        migrations.AddField(
            model_name='sarafprofile',
            name='saraf_logo',
            field=models.ImageField(blank=True, null=True, upload_to='saraf_photos/'),
        ),
        migrations.AddField(
            model_name='sarafprofile',
            name='saraf_logo_wallpeper',
            field=models.ImageField(blank=True, null=True, upload_to='saraf_photos/'),
        ),
        migrations.AddField(
            model_name='sarafprofile',
            name='licence_photo',
            field=models.ImageField(blank=True, null=True, upload_to='saraf_photos/'),
        ),
        # Copy data from old fields to new fields
        migrations.RunPython(copy_photo_fields, noop_reverse),
        # Remove old fields and about_hawala
        migrations.RemoveField(
            model_name='sarafprofile',
            name='id_card_front_photo',
        ),
        migrations.RemoveField(
            model_name='sarafprofile',
            name='id_card_back_photo',
        ),
        migrations.RemoveField(
            model_name='sarafprofile',
            name='selfie_photo',
        ),
        migrations.RemoveField(
            model_name='sarafprofile',
            name='about_hawala',
        ),
    ]
