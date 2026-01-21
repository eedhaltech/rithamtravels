# Generated migration for adding user field to Testimonial model

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('enquiries', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='testimonial',
            name='user',
            field=models.OneToOneField(
                null=True, 
                blank=True,
                on_delete=django.db.models.deletion.CASCADE, 
                related_name='testimonial', 
                to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AlterField(
            model_name='testimonial',
            name='is_approved',
            field=models.BooleanField(default=True),
        ),
    ]