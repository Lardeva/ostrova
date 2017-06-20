from decimal import Decimal
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Sum

from ostrovaweb.utils import nvl, AdminURLMixin


class Cashdesk(AdminURLMixin, models.Model):
    id = models.AutoField(primary_key=True, verbose_name="Номер")
    rec_date = models.DateField(blank=True, null=True,verbose_name="Дата")
    beg_bank_100 = models.DecimalField( max_digits=8, decimal_places=0, blank=True, null=True, verbose_name="Банкноти по 100", validators=[MinValueValidator(Decimal('0'))])
    beg_bank_50 = models.DecimalField( max_digits=8, decimal_places=0, blank=True, null=True, verbose_name="Банкноти по 50", validators=[MinValueValidator(Decimal('0'))])
    beg_bank_20 = models.DecimalField( max_digits=8, decimal_places=0, blank=True, null=True, verbose_name="Банкноти по 20", validators=[MinValueValidator(Decimal('0'))])
    beg_bank_10 = models.DecimalField( max_digits=8, decimal_places=0, blank=True, null=True, verbose_name="Банкноти по 10", validators=[MinValueValidator(Decimal('0'))])
    beg_bank_5 = models.DecimalField( max_digits=8, decimal_places=0, blank=True, null=True, verbose_name="Банкноти по 5", validators=[MinValueValidator(Decimal('0'))])
    beg_bank_2 = models.DecimalField( max_digits=8, decimal_places=0, blank=True, null=True, verbose_name="Банкноти по 2", validators=[MinValueValidator(Decimal('0'))])
    beg_coin_100 = models.DecimalField( max_digits=8, decimal_places=0, blank=True, null=True, verbose_name="Стотинки по 100", validators=[MinValueValidator(Decimal('0'))])
    beg_coin_50 = models.DecimalField( max_digits=8, decimal_places=0, blank=True, null=True, verbose_name="Стотинки по 50", validators=[MinValueValidator(Decimal('0'))])
    beg_coin_20 = models.DecimalField( max_digits=8, decimal_places=0,  blank=True, null=True, verbose_name="Стотинки по 20", validators=[MinValueValidator(Decimal('0'))])
    beg_coin_10 = models.DecimalField( max_digits=8, decimal_places=0,blank=True, null=True, verbose_name="Стотинки по 10", validators=[MinValueValidator(Decimal('0'))])
    beg_coin_5 = models.DecimalField( max_digits=8, decimal_places=0, blank=True, null=True, verbose_name="Стотинки по 5", validators=[MinValueValidator(Decimal('0'))])
    beg_coin_2 = models.DecimalField( max_digits=8, decimal_places=0, blank=True, null=True, verbose_name=" Стотинки по 2", validators=[MinValueValidator(Decimal('0'))])
    beg_coin_1 = models.DecimalField( max_digits=8, decimal_places=0, blank=True, null=True, verbose_name=" Стотинки по 1", validators=[MinValueValidator(Decimal('0'))])
    beg_close = models.ForeignKey(User, blank=True, null=True,related_name='beg_close', verbose_name="Предал")
    beg_open = models.ForeignKey(User, blank=True, null=True, related_name='beg_open', verbose_name="Приел")
    beg_close_date = models.DateField(blank=True, null=True, verbose_name="Дата на предаване")
    beg_open_date = models.DateField(blank=True, null=True, verbose_name="Дата на приемане")
    end_bank_100 =models.DecimalField( max_digits=8, decimal_places=0, blank=True, null=True, verbose_name="Банкноти по 100", validators=[MinValueValidator(Decimal('0'))])
    end_bank_50 = models.DecimalField( max_digits=8, decimal_places=0, blank=True, null=True, verbose_name="Банкноти по 50", validators=[MinValueValidator(Decimal('0'))])
    end_bank_20 = models.DecimalField( max_digits=8, decimal_places=0, blank=True, null=True, verbose_name="Банкноти по 20", validators=[MinValueValidator(Decimal('0'))])
    end_bank_10 = models.DecimalField( max_digits=8, decimal_places=0, blank=True, null=True, verbose_name="Банкноти по 10", validators=[MinValueValidator(Decimal('0'))])
    end_bank_5 = models.DecimalField( max_digits=8, decimal_places=0, blank=True, null=True, verbose_name="Банкноти по 5", validators=[MinValueValidator(Decimal('0'))])
    end_bank_2 = models.DecimalField( max_digits=8, decimal_places=0, blank=True, null=True, verbose_name="Банкноти по 2", validators=[MinValueValidator(Decimal('0'))])
    end_coin_100 = models.DecimalField( max_digits=8, decimal_places=0, blank=True, null=True, verbose_name="Стотинки по 100", validators=[MinValueValidator(Decimal('0'))])
    end_coin_50 = models.DecimalField( max_digits=8, decimal_places=0, blank=True, null=True, verbose_name="Стотинки по 50", validators=[MinValueValidator(Decimal('0'))])
    end_coin_20 = models.DecimalField( max_digits=8, decimal_places=0, blank=True, null=True, verbose_name="Стотинки по 20", validators=[MinValueValidator(Decimal('0'))])
    end_coin_10 = models.DecimalField( max_digits=8, decimal_places=0, blank=True, null=True, verbose_name="Стотинки по 10", validators=[MinValueValidator(Decimal('0'))])
    end_coin_5 = models.DecimalField( max_digits=8, decimal_places=0, blank=True, null=True, verbose_name=" Стотинки по 5", validators=[MinValueValidator(Decimal('0'))])
    end_coin_2 = models.DecimalField( max_digits=8, decimal_places=0, blank=True, null=True, verbose_name=" Стотинки по 2", validators=[MinValueValidator(Decimal('0'))])
    end_coin_1 = models.DecimalField( max_digits=8, decimal_places=0, blank=True, null=True, verbose_name=" Стотинки по 1", validators=[MinValueValidator(Decimal('0'))])
    club_fk = models.ForeignKey('nomenclature.Club', null=True, verbose_name="Обект")
    create_date = models.DateTimeField(blank=True, null=True, verbose_name="Дата на създавне")
    last_update_date = models.DateTimeField(blank=True, null=True,verbose_name="Дата на промяна")
    status = models.CharField(max_length=80, verbose_name="Статус", choices = (
        ('OPENED', 'ОТВОРЕНА'),
        ('JUSTCLOSED', 'ПОСЛЕДНО ЗАТВОРЕНА'),
        ('CLOSED', 'ЗАТВОРЕНА'),
       ), default='OPENED')

    @property
    def beg_amount(self):
        return round(nvl(self.beg_coin_1,0 * Decimal(0.01)) +
                nvl(self.beg_coin_2,0 * Decimal(0.02)) +
                nvl(self.beg_coin_5,0 * Decimal(0.05)) +
                nvl(self.beg_coin_10,0) * Decimal(0.1)+
                nvl(self.beg_coin_20,0) * Decimal(0.2) +
                nvl(self.beg_coin_50,0) * Decimal(0.5) +
                nvl(self.beg_coin_100,0) * 1 +
                nvl(self.beg_bank_2,0) * 2 +
                nvl(self.beg_bank_5,0) * 5 +
                nvl(self.beg_bank_10,0) * 10 +
                nvl(self.beg_bank_20,0) * 20 +
                nvl(self.beg_bank_50,0) * 50 +
                nvl(self.beg_bank_100,0) * 100, 2 )
    beg_amount.fget.short_description = 'Сума в началото на деня'

    @property
    def end_amount(self):
        return round(nvl(self.end_coin_1,0) * Decimal(0.01) +
                nvl(self.end_coin_2,0) * Decimal(0.02) +
                nvl(self.end_coin_5,0) * Decimal(0.05) +
                nvl(self.end_coin_10,0) * Decimal(0.1) +
                nvl(self.end_coin_20,0) * Decimal(0.2) +
                nvl(self.end_coin_50,0) * Decimal(0.5) +
                nvl(self.end_coin_100,0) * 1 +
                nvl(self.end_bank_2,0) * 2 +
                nvl(self.end_bank_5,0) * 5 +
                nvl(self.end_bank_10,0) * 10 +
                nvl(self.end_bank_20,0) * 20 +
                nvl(self.end_bank_50,0) * 50 +
                nvl(self.end_bank_100,0) * 100 ,2)
    end_amount.fget.short_description = 'Очаквана сума в края на деня'


    @property
    def amt_header(self):
        return ''
    amt_header.fget.short_description = 'Суми'

    @property
    def total_amount(self):
        return self.beg_amount + self.income_amount - self.expense_amount
    total_amount.fget.short_description = 'Общо сума'

    @property
    def income_amount(self):
        result = Cashdesk_detail_income.objects.filter(cashdesk=self).aggregate(Sum('amount'))
        return nvl(result['amount__sum'],0)
    income_amount.fget.short_description = 'Сума приход'

    @property
    def expense_amount(self):
        result = Cashdesk_detail_expense.objects.filter(cashdesk=self).aggregate(Sum('amount'))
        return nvl(result['amount__sum'],0)
    expense_amount.fget.short_description = 'Сума разход'

    class Meta:
        managed = True
        db_table = 'cashdesk'
        verbose_name = u"Каса"
        verbose_name_plural = u"Каси"

    def __str__(self):
        return str(self.id) + ":" + str(self.club_fk) + ":" + str(self.rec_date)


class Cashdesk_detail_income(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="Номер")
    cashdesk = models.ForeignKey('Cashdesk', verbose_name="Каса", limit_choices_to={'status':'OPENED'})
    order_fk = models.ForeignKey('order.Order', blank=True, null=True, verbose_name="Плащане по поръчка")
    group_fk = models.ForeignKey('nomenclature.Cashdesk_groups_income', verbose_name="Група приходи")
    note = models.CharField(max_length=400, blank=True, null=True, verbose_name="Забележка")
    amount = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Сума", validators=[MinValueValidator(Decimal('0.01'))])
    transfer_fk = models.ForeignKey('Cashdesk_detail_expense', blank=True, null=True, verbose_name="Трансфер")
    transfer_club_fk = models.ForeignKey('nomenclature.Club',blank=True, null=True, verbose_name="Към обект", related_name='cashdesk_detail_income_transfer_set')

    class Meta:
        managed = True
        db_table = 'cashdesk_detail_income'
        verbose_name = u"Приходен касов ордер"
        verbose_name_plural = u"Приходни касови ордери"

    def __str__(self):
        return str(self.cashdesk) + ":ПРИХОД:" + str(self.note) + ":" + str(self.amount)


class Cashdesk_detail_expense(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="Номер")
    cashdesk = models.ForeignKey('Cashdesk', verbose_name="Каса", limit_choices_to={'status':'OPENED'})
    delivery_fk = models.ForeignKey('delivery.Delivery', blank=True, null=True, verbose_name="Плащане по доставка")
    group_fk = models.ForeignKey('nomenclature.Cashdesk_groups_expense', verbose_name="Група разходи")
    note = models.CharField(max_length=400, blank=True, null=True, verbose_name="Забележка")
    amount = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Сума", validators=[MinValueValidator(Decimal('0.01'))])
    transfer_fk = models.ForeignKey('Cashdesk_detail_income', blank=True, null=True, verbose_name="Трансфер")
    transfer_club_fk = models.ForeignKey('nomenclature.Club',blank=True, null=True, verbose_name="Към обект", related_name='cashdesk_detail_expense_transfer_set')

    class Meta:
        managed = True
        db_table = 'cashdesk_detail_expense'
        verbose_name = u"Разходен касов ордер"
        verbose_name_plural = u"Разходни касови ордери"

    def __str__(self):
        return str(self.cashdesk) + ":РАЗХОД:" + str(self.note) + ":" + str(self.amount)

class Cashdesk_detail_transfer(Cashdesk_detail_expense):
    class Meta:
        proxy = True
        verbose_name = u"Касов трансфер"
        verbose_name_plural = u"Касови трансфери"

    def __str__(self):
        return str(self.cashdesk) + ":ТРАНСФЕР:" + str(self.note) + ":" + str(self.amount)