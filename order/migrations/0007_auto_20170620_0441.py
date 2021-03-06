# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2017-06-20 01:41
from __future__ import unicode_literals

from decimal import Decimal
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cashdesk', '0004_auto_20170620_0441'),
        ('order', '0006_auto_20170619_1236'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='cashdesk_deposit2_fk',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='order_deposit2', to='cashdesk.Cashdesk', verbose_name='Платено в каса'),
        ),
        migrations.AddField(
            model_name='order',
            name='cashdesk_deposit_fk',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='order_deposit', to='cashdesk.Cashdesk', verbose_name='Платено в каса'),
        ),
        migrations.AddField(
            model_name='order',
            name='cashdesk_payment_fk',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='order_final_payment', to='cashdesk.Cashdesk', verbose_name='Платено в каса'),
        ),
        migrations.AddField(
            model_name='order',
            name='deposit2_payment_type',
            field=models.CharField(choices=[('CASH', 'В БРОЙ'), ('BANK_TRANSFER', 'БАНКОВ ПРЕВОД'), ('BANK_CARD', 'ПЛАЩАНЕ С КАРТА')], default='CASH', max_length=30, verbose_name='Тип на плащане'),
        ),
        migrations.AddField(
            model_name='order',
            name='deposit_payment_type',
            field=models.CharField(choices=[('CASH', 'В БРОЙ'), ('BANK_TRANSFER', 'БАНКОВ ПРЕВОД'), ('BANK_CARD', 'ПЛАЩАНЕ С КАРТА')], default='CASH', max_length=30, verbose_name='Тип на плащане'),
        ),
        migrations.AddField(
            model_name='order',
            name='final_payment_type',
            field=models.CharField(choices=[('CASH', 'В БРОЙ'), ('BANK_TRANSFER', 'БАНКОВ ПРЕВОД'), ('BANK_CARD', 'ПЛАЩАНЕ С КАРТА')], default='CASH', max_length=30, verbose_name='Тип на плащане'),
        ),
        migrations.AlterField(
            model_name='order',
            name='deposit',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))], verbose_name='Капаро'),
        ),
        migrations.AlterField(
            model_name='order',
            name='deposit2',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))], verbose_name='Капаро 2'),
        ),
        migrations.AlterField(
            model_name='order',
            name='payed_final',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))], verbose_name='Финално плащане'),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('REQUESTED', 'ЗАЯВЕНА'), ('CONFIRMED', 'ПОТВЪРДЕНА'), ('ORDERED', 'ПОРЪЧАНА'), ('CANCELED', 'ОТКАЗАНА')], default='REQUESTED', max_length=80, verbose_name='Статус'),
        ),
        migrations.AlterField(
            model_name='orderdetail',
            name='cnt',
            field=models.DecimalField(decimal_places=3, max_digits=8, validators=[django.core.validators.MinValueValidator(Decimal('0.001'))], verbose_name='Количество'),
        ),
        migrations.AlterField(
            model_name='orderdetail',
            name='price',
            field=models.DecimalField(decimal_places=2, max_digits=8, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))], verbose_name='Единична цена'),
        ),
    ]
