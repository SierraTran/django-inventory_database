# Generated by Django 5.1.5 on 2025-02-24 14:58

import django.db.models.deletion
import django.utils.timezone
import model_utils.fields
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0012_useditem'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='description_changed_at',
            field=model_utils.fields.MonitorField(default=django.utils.timezone.now, monitor='description'),
        ),
        migrations.AddField(
            model_name='item',
            name='location_changed_at',
            field=model_utils.fields.MonitorField(default=django.utils.timezone.now, monitor='location'),
        ),
        migrations.AddField(
            model_name='item',
            name='manufacturer_changed_at',
            field=model_utils.fields.MonitorField(default=django.utils.timezone.now, monitor='manufacturer'),
        ),
        migrations.AddField(
            model_name='item',
            name='min_quantity_changed_at',
            field=model_utils.fields.MonitorField(default=django.utils.timezone.now, monitor='min_quantity'),
        ),
        migrations.AddField(
            model_name='item',
            name='model_changed_at',
            field=model_utils.fields.MonitorField(default=django.utils.timezone.now, monitor='model'),
        ),
        migrations.AddField(
            model_name='item',
            name='modified_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='item',
            name='part_number_changed_at',
            field=model_utils.fields.MonitorField(default=django.utils.timezone.now, monitor='part_number'),
        ),
        migrations.AddField(
            model_name='item',
            name='part_or_unit_changed_at',
            field=model_utils.fields.MonitorField(default=django.utils.timezone.now, monitor='part_or_unit'),
        ),
        migrations.AddField(
            model_name='item',
            name='quantity_changed_at',
            field=model_utils.fields.MonitorField(default=django.utils.timezone.now, monitor='quantity'),
        ),
        migrations.AddField(
            model_name='item',
            name='unit_price_changed_at',
            field=model_utils.fields.MonitorField(default=django.utils.timezone.now, monitor='unit_price'),
        ),
        migrations.AddField(
            model_name='itemrequest',
            name='timestamp',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='itemrequest',
            name='status',
            field=model_utils.fields.StatusField(choices=[('Pending', 'Pending'), ('Accepted', 'Accepted'), ('Rejected', 'Rejected')], db_index=True, default='Pending', max_length=100, no_check_for_status=True),
        ),
        migrations.CreateModel(
            name='ItemHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(choices=[('create', 'Create'), ('update', 'Update'), ('delete', 'Delete')], max_length=6)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('changes', models.TextField(blank=True, null=True)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.item')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
