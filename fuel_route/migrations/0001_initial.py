# Generated by Django 3.2.23 on 2024-10-08 12:26

import django.contrib.gis.db.models.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FuelStationModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('opis_id', models.IntegerField(unique=True)),
                ('name', models.CharField(max_length=255)),
                ('address', models.CharField(max_length=255)),
                ('city', models.CharField(max_length=100)),
                ('state', models.CharField(max_length=2)),
                ('location', django.contrib.gis.db.models.fields.PointField(srid=4326)),
                ('price', models.FloatField()),
            ],
        ),
        migrations.AddIndex(
            model_name='fuelstationmodel',
            index=models.Index(fields=['location'], name='fuel_route__locatio_194c86_idx'),
        ),
    ]
