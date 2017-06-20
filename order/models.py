from decimal import Decimal, Context
from django.contrib.auth.models import User
from django.core.validators import EmailValidator, MinValueValidator
from django.db import models
from django.db.models import F, Sum
from django.utils import formats
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField

from nomenclature.models import Article
from ostrovaweb.utils import nvl


class Order(models.Model):
    PAYMENT_TYPES = (
        ('CASH', 'В БРОЙ'),
        ('BANK_TRANSFER', 'БАНКОВ ПРЕВОД'),
        ('BANK_CARD', 'ПЛАЩАНЕ С КАРТА'),
    )

    id = models.AutoField(primary_key=True, verbose_name="Номер")

    rec_date = models.DateField(verbose_name="Дата на р.д.")
    rec_time = models.TimeField(verbose_name="Начало")
    rec_time_end = models.TimeField(verbose_name="Край")

    club_fk = models.ForeignKey('nomenclature.Club', null=True, verbose_name="Клуб")
    saloon_fk = models.ForeignKey('nomenclature.Saloon', verbose_name="Салон за възрастни",blank=False, null=True)

    phone = PhoneNumberField(max_length=100, blank=True, null=True, verbose_name="Телефон")
    parent = models.CharField(max_length=240, blank=True, null=True, verbose_name="Родител")
    child = models.CharField(max_length=200, blank=True, null=True, verbose_name="Дете")
    age = models.IntegerField(blank=True, null=True, verbose_name="Години")
    child_count = models.IntegerField(blank=True, null=True, verbose_name="Брой деца")
    adult_count = models.IntegerField(blank=True, null=True, verbose_name="Брой възрастни")
    email = models.EmailField(max_length=400, blank=True, null=True, verbose_name="E-mail")
    address = models.CharField(max_length=1024, blank=True, null=True, verbose_name="Адрес")

    deposit = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True, verbose_name="Капаро", validators=[MinValueValidator(Decimal('0.01'))])
    deposit_date = models.DateField(blank=True, null=True, verbose_name="Дата на капаро")
    cashdesk_deposit_fk = models.ForeignKey('cashdesk.Cashdesk', blank=True, null=True, verbose_name="Платено в каса", related_name="order_deposit")
    deposit_payment_type = models.CharField(max_length=30, verbose_name="Тип на плащане", choices = PAYMENT_TYPES, default='CASH')

    deposit2 = models.DecimalField( max_digits=8, decimal_places=2, blank=True, null=True, verbose_name="Капаро 2", validators=[MinValueValidator(Decimal('0.01'))])
    deposit2_date = models.DateField(blank=True, null=True, verbose_name="Дата на капаро2")
    cashdesk_deposit2_fk = models.ForeignKey('cashdesk.Cashdesk', blank=True, null=True, verbose_name="Платено в каса", related_name="order_deposit2")
    deposit2_payment_type = models.CharField(max_length=30, verbose_name="Тип на плащане", choices = PAYMENT_TYPES, default='CASH')

    payment_date = models.DateField(blank=True, null=True, verbose_name="Дата на плащане")
    payed_final = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True, verbose_name="Финално плащане", validators=[MinValueValidator(Decimal('0.01'))])
    cashdesk_payment_fk = models.ForeignKey('cashdesk.Cashdesk', blank=True, null=True, verbose_name="Платено в каса", related_name="order_final_payment")
    final_payment_type = models.CharField(max_length=30, verbose_name="Тип на плащане", choices = PAYMENT_TYPES, default='CASH')

    discount = models.DecimalField( max_digits=8, decimal_places=2, blank=True, null=True, verbose_name="Отстъпка")

    # validity_date = models.DateField(blank=True, null=True, verbose_name="Дата на валидност")
    refusal_date = models.DateField(blank=True, null=True, verbose_name="Дата на отказ")
    refusal_reason = models.CharField(max_length=400, blank=True, null=True, verbose_name="Причина за отказ")

    notes = models.TextField(max_length=12000, blank=True, null=True, verbose_name="Забележка")
    notes_torta = models.TextField(max_length=2000, blank=True, null=True, verbose_name="Забележка за тортата")
    notes_kitchen = models.TextField(max_length=2000, blank=True, null=True, verbose_name="Забележка за кухнята")

    user = models.ForeignKey(User, verbose_name="Служител")
    create_date = models.DateTimeField(default=timezone.now, verbose_name="Дата на създаване")
    last_update_date = models.DateTimeField(blank=True, null=True, verbose_name="Дата на промяна")
    # changes = models.TextField(max_length=12000, blank=True, verbose_name="Промени")

    store_status = models.BooleanField(default=False, verbose_name=" Изписано от склада")
    locked = models.BooleanField(default=False, max_length=4,  verbose_name="Приключено")
    status = models.CharField(max_length=80, verbose_name="Статус", choices = (
        ('REQUESTED', 'ЗАЯВЕНА'),
        ('CONFIRMED', 'ПОТВЪРДЕНА'),
        ('ORDERED', 'ПОРЪЧАНА'),
        ('CANCELED', 'ОТКАЗАНА'),
    ), default='REQUESTED')

    def priceDetail_int(self):
        result = OrderDetail.objects.filter(order_fk=self).aggregate(agg_Result=Sum(F('cnt')*F('price')))
        return Decimal(nvl(result['agg_Result'],0))

    def priceFinal_int(self):
        return Decimal(Decimal(nvl(self.priceDetail_int(),0)) - Decimal(nvl(self.priceDetail_int(),0)) * Decimal(nvl(self.discount,0)) / Decimal(100))

    def dueAmount_int(self):
        return Decimal(Decimal(nvl(self.priceFinal_int(),0)) - Decimal(nvl(self.deposit2,0)) - Decimal(nvl(self.deposit,0)) - Decimal(nvl(self.payed_final,0)))

    @property
    def priceDetail(self):
        return formats.number_format(self.priceDetail_int(),2)
    priceDetail.fget.short_description = 'Цена'

    @property
    def priceFinal(self):
        return  formats.number_format(self.priceFinal_int(),2)
    priceFinal.fget.short_description = 'Крайна цена'

    @property
    def dueAmount(self):
        return formats.number_format(self.dueAmount_int(),2)
    dueAmount.fget.short_description = 'Сума за доплащане'

    def __str__(self):
        return str(nvl(self.parent,'')) + ":" + str(nvl(self.phone,'')) + ":" + str(nvl(self.child,'')) + " :" + str(nvl(self.deposit,0)) + " лв."


    class Meta:
        managed = True
        db_table = 'order'
        verbose_name = u"Поръчка"
        verbose_name_plural = u"Поръчки"


class OrderDetail(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="Номер")
    order_fk = models.ForeignKey('Order', null=True, verbose_name="Поръчка N")
    article_fk = models.ForeignKey('ArticleOrder', blank=False, null=False, verbose_name="Артикул")
    cnt = models.DecimalField(max_digits=8, decimal_places=3,verbose_name="Количество", validators=[MinValueValidator(Decimal('0.001'))])
    price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Единична цена", validators=[MinValueValidator(Decimal('0.01'))])
    amount = models.DecimalField( max_digits=8, decimal_places=2, verbose_name="Общо", blank=True, null=False)

    def __str__(self):
        return self.article_fk.group_fk.name + ":" + self.article_fk.name + ":" + str(self.cnt) + " " + self.article_fk.measure + " :" + str(self.price) + " лв."

    class Meta:
        managed = True
        db_table = 'order_detail'
        verbose_name = u"Поръчка описание"
        verbose_name_plural = u"Поръчки описание"


class ArticleOrderManager(models.Manager):
    def get_queryset(self):
        return super(ArticleOrderManager, self).get_queryset().filter(active=True, sale_price__gte=0)


class ArticleOrder(Article):
    objects = ArticleOrderManager()

    class Meta:
        proxy = True
        verbose_name = u"Артикул продажби"
        verbose_name_plural = u"Артикули продажби"
