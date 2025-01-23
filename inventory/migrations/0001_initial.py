# Generated by Django 5.1.5 on 2025-01-23 20:52

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='item',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('manufacturer', models.CharField(max_length=50)),
                ('model', models.CharField(max_length=100)),
                ('part_or_unit', models.CharField(choices=[('Part', 'Part'), ('Unit', 'Unit')], max_length=10)),
                ('description', models.TextField()),
                ('location', models.CharField(max_length=50)),
                ('quantity', models.IntegerField()),
                ('price', models.CharField(max_length=255)),
            ],
        ),
    ]
