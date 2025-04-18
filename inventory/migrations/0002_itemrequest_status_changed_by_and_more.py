# Generated by Django 5.1.5 on 2025-03-25 17:55

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='itemrequest',
            name='status_changed_by',
            field=models.ForeignKey(default=None, limit_choices_to={'groups__name': 'Superuser'}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='status_changed_by_user', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='itemrequest',
            name='requested_by',
            field=models.ForeignKey(limit_choices_to={'groups__name': 'Technician'}, on_delete=django.db.models.deletion.CASCADE, related_name='requested_by_user', to=settings.AUTH_USER_MODEL),
        ),
    ]
