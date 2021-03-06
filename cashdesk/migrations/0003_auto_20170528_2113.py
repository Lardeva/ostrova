# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2017-05-28 18:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cashdesk', '0002_auto_20170509_0110'),
    ]

    operations = [
        migrations.AddField(
            model_name='cashdesk',
            name='beg_coin_1',
            field=models.DecimalField(blank=True, decimal_places=0, max_digits=8, null=True, verbose_name=' Стотинки по 1'),
        ),
        migrations.AddField(
            model_name='cashdesk',
            name='beg_coin_2',
            field=models.DecimalField(blank=True, decimal_places=0, max_digits=8, null=True, verbose_name=' Стотинки по 2'),
        ),
        migrations.AddField(
            model_name='cashdesk',
            name='end_coin_1',
            field=models.DecimalField(blank=True, decimal_places=0, max_digits=8, null=True, verbose_name=' Стотинки по 1'),
        ),
        migrations.AddField(
            model_name='cashdesk',
            name='end_coin_2',
            field=models.DecimalField(blank=True, decimal_places=0, max_digits=8, null=True, verbose_name=' Стотинки по 2'),
        ),
        migrations.AlterField(
            model_name='cashdesk',
            name='beg_bank_10',
            field=models.DecimalField(blank=True, decimal_places=0, max_digits=8, null=True, verbose_name='Банкноти по 10'),
        ),
        migrations.AlterField(
            model_name='cashdesk',
            name='beg_bank_100',
            field=models.DecimalField(blank=True, decimal_places=0, max_digits=8, null=True, verbose_name='Банкноти по 100'),
        ),
        migrations.AlterField(
            model_name='cashdesk',
            name='beg_bank_2',
            field=models.DecimalField(blank=True, decimal_places=0, max_digits=8, null=True, verbose_name='Банкноти по 2'),
        ),
        migrations.AlterField(
            model_name='cashdesk',
            name='beg_bank_20',
            field=models.DecimalField(blank=True, decimal_places=0, max_digits=8, null=True, verbose_name='Банкноти по 20'),
        ),
        migrations.AlterField(
            model_name='cashdesk',
            name='beg_bank_5',
            field=models.DecimalField(blank=True, decimal_places=0, max_digits=8, null=True, verbose_name='Банкноти по 5'),
        ),
        migrations.AlterField(
            model_name='cashdesk',
            name='beg_bank_50',
            field=models.DecimalField(blank=True, decimal_places=0, max_digits=8, null=True, verbose_name='Банкноти по 50'),
        ),
        migrations.AlterField(
            model_name='cashdesk',
            name='beg_coin_10',
            field=models.DecimalField(blank=True, decimal_places=0, max_digits=8, null=True, verbose_name='Стотинки по 10'),
        ),
        migrations.AlterField(
            model_name='cashdesk',
            name='beg_coin_100',
            field=models.DecimalField(blank=True, decimal_places=0, max_digits=8, null=True, verbose_name='Стотинки по 100'),
        ),
        migrations.AlterField(
            model_name='cashdesk',
            name='beg_coin_20',
            field=models.DecimalField(blank=True, decimal_places=0, max_digits=8, null=True, verbose_name='Стотинки по 20'),
        ),
        migrations.AlterField(
            model_name='cashdesk',
            name='beg_coin_5',
            field=models.DecimalField(blank=True, decimal_places=0, max_digits=8, null=True, verbose_name='Стотинки по 5'),
        ),
        migrations.AlterField(
            model_name='cashdesk',
            name='beg_coin_50',
            field=models.DecimalField(blank=True, decimal_places=0, max_digits=8, null=True, verbose_name='Стотинки по 50'),
        ),
        migrations.AlterField(
            model_name='cashdesk',
            name='end_bank_10',
            field=models.DecimalField(blank=True, decimal_places=0, max_digits=8, null=True, verbose_name='Банкноти по 10'),
        ),
        migrations.AlterField(
            model_name='cashdesk',
            name='end_bank_100',
            field=models.DecimalField(blank=True, decimal_places=0, max_digits=8, null=True, verbose_name='Банкноти по 100'),
        ),
        migrations.AlterField(
            model_name='cashdesk',
            name='end_bank_2',
            field=models.DecimalField(blank=True, decimal_places=0, max_digits=8, null=True, verbose_name='Банкноти по 2'),
        ),
        migrations.AlterField(
            model_name='cashdesk',
            name='end_bank_20',
            field=models.DecimalField(blank=True, decimal_places=0, max_digits=8, null=True, verbose_name='Банкноти по 20'),
        ),
        migrations.AlterField(
            model_name='cashdesk',
            name='end_bank_5',
            field=models.DecimalField(blank=True, decimal_places=0, max_digits=8, null=True, verbose_name='Банкноти по 5'),
        ),
        migrations.AlterField(
            model_name='cashdesk',
            name='end_bank_50',
            field=models.DecimalField(blank=True, decimal_places=0, max_digits=8, null=True, verbose_name='Банкноти по 50'),
        ),
        migrations.AlterField(
            model_name='cashdesk',
            name='end_coin_10',
            field=models.DecimalField(blank=True, decimal_places=0, max_digits=8, null=True, verbose_name='Стотинки по 10'),
        ),
        migrations.AlterField(
            model_name='cashdesk',
            name='end_coin_100',
            field=models.DecimalField(blank=True, decimal_places=0, max_digits=8, null=True, verbose_name='Стотинки по 100'),
        ),
        migrations.AlterField(
            model_name='cashdesk',
            name='end_coin_20',
            field=models.DecimalField(blank=True, decimal_places=0, max_digits=8, null=True, verbose_name='Стотинки по 20'),
        ),
        migrations.AlterField(
            model_name='cashdesk',
            name='end_coin_5',
            field=models.DecimalField(blank=True, decimal_places=0, max_digits=8, null=True, verbose_name=' Стотинки по 5'),
        ),
        migrations.AlterField(
            model_name='cashdesk',
            name='end_coin_50',
            field=models.DecimalField(blank=True, decimal_places=0, max_digits=8, null=True, verbose_name='Стотинки по 50'),
        ),
    ]
