# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2017-06-20 09:08
from __future__ import unicode_literals

from decimal import Decimal
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0008_auto_20170620_0658'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='discount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0'))], verbose_name='Отстъпка'),
        ),
    ]
