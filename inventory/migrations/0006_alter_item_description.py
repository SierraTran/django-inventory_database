# Generated by Django 5.1.5 on 2025-03-05 15:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0005_remove_itemrequest_item_itemrequest_description_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='description',
            field=models.TextField(blank=True),
        ),
    ]
