# Generated by Django 5.1.4 on 2025-02-12 10:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0013_product_toka_baridi_product_toka_moto'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='pokelewa_mgando',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='product',
            name='toka_mgando',
            field=models.FloatField(default=0),
        ),
    ]
