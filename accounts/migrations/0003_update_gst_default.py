# Generated migration to update GST default setting

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_alter_user_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='systemsettings',
            name='gst_enabled',
            field=models.BooleanField(default=False, help_text='Apply GST to bookings'),
        ),
        # Update existing SystemSettings instance to have GST disabled by default
        migrations.RunSQL(
            "UPDATE accounts_systemsettings SET gst_enabled = false WHERE id = 1;",
            reverse_sql="UPDATE accounts_systemsettings SET gst_enabled = true WHERE id = 1;"
        ),
    ]