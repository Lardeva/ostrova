# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2017-05-28 18:13
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('delivery', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='deliverydetail',
            name='amount',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=8, verbose_name='Цена'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='delivery',
            name='cashdesk_fk',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='cashdesk.Cashdesk', verbose_name='Платено в каса'),
        ),
        migrations.AlterField(
            model_name='delivery',
            name='paid',
            field=models.CharField(choices=[('No', 'НЕ'), ('Yes', 'ДА')], default='No', max_length=80, verbose_name='Платено'),
        ),
    ]
