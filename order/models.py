from decimal import Decimal
from django.contrib.auth.models import User
from django.db import models
from django.db.models import F, Sum
from django.utils import timezone

from nomenclature.models import Article
from ostrovaweb.utils import nvl


class Order(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="Номер")
    rec_date = models.DateField(verbose_name="Дата на р.д.")
    rec_time = models.TimeField(verbose_name="Начало")
    rec_time_end = models.TimeField(verbose_name="Край")
    phone = models.CharField(max_length=100, blank=True, verbose_name="Телефон")
    parent = models.CharField(max_length=240, blank=True, verbose_name="Родител")
    child = models.CharField(max_length=200, blank=True, verbose_name="Дете")
    age = models.IntegerField(blank=True, null=True, verbose_name="Години")
    child_count = models.IntegerField(blank=True, null=True, verbose_name="Брой деца")
    adult_count = models.IntegerField(blank=True, null=True, verbose_name="Брой възрастни")
    saloon_fk = models.ForeignKey('nomenclature.Saloon', verbose_name="Салон за възрастни",blank=False, null=True)
    # hall_count = models.IntegerField(blank=True, null=True, verbose_name="Брой зала")
    # hall_price = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True, verbose_name="Цена на зала")
    deposit = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True, verbose_name="Капаро")
    discount = models.DecimalField( max_digits=8, decimal_places=2, blank=True, null=True, verbose_name="Отстъпка")
    #price_final = models.DecimalField( max_digits=8, decimal_places=2, blank=True, null=True, verbose_name="Крайна цена")
    deposit_date = models.DateField(blank=True, null=True, verbose_name="Дата на капаро")
    payment_date = models.DateField(blank=True, null=True, verbose_name="Дата на плащане")
    # validity_date = models.DateField(blank=True, null=True, verbose_name="Дата на валидност")
    refusal_date = models.DateField(blank=True, null=True, verbose_name="Дата на отказ")
    refusal_reason = models.CharField(max_length=400, blank=True, verbose_name="Причина за отказ")
    notes = models.TextField(max_length=12000, blank=True, verbose_name="Забележка")
    address = models.CharField(max_length=1024, blank=True, verbose_name="Адрес")
    user = models.ForeignKey(User, verbose_name="Служител")
    email = models.CharField(max_length=400, blank=True, verbose_name="E-mail")
    club_fk = models.ForeignKey('nomenclature.Club', null=True, verbose_name="Клуб")
    create_date = models.DateTimeField(default=timezone.now, verbose_name="Дата на създаване")
    last_update_date = models.DateTimeField(blank=True, null=True, verbose_name="Дата на промяна")
    # changes = models.TextField(max_length=12000, blank=True, verbose_name="Промени")
    deposit2 = models.DecimalField( max_digits=8, decimal_places=2, blank=True, null=True, verbose_name="Капаро 2")
    deposit2_date = models.DateField(blank=True, null=True, verbose_name="Дата на капаро2")
    locked = models.BooleanField(default=False, max_length=4,  verbose_name="Приключено")
    payed_final = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True, verbose_name="Финално плащане")
    notes_torta = models.TextField(max_length=2000, blank=True, verbose_name="Забележка за тортата")
    notes_kitchen = models.TextField(max_length=2000, blank=True, verbose_name="Забележка за кухнята")
    store_status = models.BooleanField(default=False, verbose_name=" Изписано от склада")
    status = models.CharField(max_length=80, verbose_name="Статус", choices = (
        ('REQUESTED', 'ЗАЯВЕНА'),
        ('CONFIRMED', 'ПОТВЪРДЕНА'),
        ('ORDERED', 'ПОРЪЧАНА'),
        ('CANCELED', 'ОТКАЗАНА'),
    ), default='REQUIRED')


    @property
    def priceDetail(self):
        result = OrderDetail.objects.filter(order_fk=self).aggregate(agg_Result=Sum(F('cnt')*F('price')))
        return Decimal(nvl(result['agg_Result'],0))
    priceDetail.fget.short_description = 'Цена'

    @property
    def priceFinal(self):
        return  Decimal(nvl(self.priceDetail,0)) - Decimal(nvl(self.priceDetail,0)) * Decimal(nvl(self.discount,0)) / Decimal(100)
    priceFinal.fget.short_description = 'Крайна цена'

    @property
    def dueAmount(self):
        return Decimal(nvl(self.priceFinal,0)) - Decimal(nvl(self.deposit2,0)) - Decimal(nvl(self.deposit,0)) - Decimal(nvl(self.payed_final,0))
    dueAmount.fget.short_description = 'Сума за доплащане'

    def __str__(self):
        return str(self.parent) + ":" + str(self.phone) + ":" + str(self.child) + " :" + str(self.deposit) + " лв."


    class Meta:
        managed = True
        db_table = 'order'
        verbose_name = u"Поръчка"
        verbose_name_plural = u"Поръчки"


class OrderDetail(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="Номер")
    order_fk = models.ForeignKey('Order', null=True, verbose_name="Поръчка N")
    article_fk = models.ForeignKey('ArticleOrder', blank=False, null=False, verbose_name="Артикул")
    cnt = models.DecimalField(max_digits=8, decimal_places=3,verbose_name="Количество")
    price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Единична цена")
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
