# Generated by Django 5.1.5 on 2025-02-24 16:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0013_item_description_changed_at_item_location_changed_at_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='item',
            name='description_changed_at',
        ),
        migrations.RemoveField(
            model_name='item',
            name='location_changed_at',
        ),
        migrations.RemoveField(
            model_name='item',
            name='manufacturer_changed_at',
        ),
        migrations.RemoveField(
            model_name='item',
            name='min_quantity_changed_at',
        ),
        migrations.RemoveField(
            model_name='item',
            name='model_changed_at',
        ),
        migrations.RemoveField(
            model_name='item',
            name='part_number_changed_at',
        ),
        migrations.RemoveField(
            model_name='item',
            name='part_or_unit_changed_at',
        ),
        migrations.RemoveField(
            model_name='item',
            name='quantity_changed_at',
        ),
        migrations.RemoveField(
            model_name='item',
            name='unit_price_changed_at',
        ),
    ]
