from decimal import Decimal
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone
from django.db.models import F, Sum

from nomenclature.models import Article
from ostrovaweb.utils import nvl


class Delivery(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="Номер")
    order_date = models.DateField( verbose_name="Дата на заявка", default=timezone.now)
    supplier_fk = models.ForeignKey('nomenclature.Supplier', verbose_name="Доставчик")
    status = models.CharField(max_length=80, verbose_name="Статус", choices = (
        ('ORDERED', 'ПОРЪЧАНO'),
        ('DELIVERED', 'ДОСТАВЕНО'),
        ('CANCELED', 'ОТКАЗАНО'),
    ), default='ORDERED')
    user = models.ForeignKey(User, verbose_name="Служител")
    delivery_date = models.DateField(blank=True, null=True, verbose_name="Дата на доставка")
    invoice_no = models.CharField(max_length=400, blank=True, null=True, verbose_name="Номер на фактура")
    firm_invoice_no = models.CharField(max_length=400, blank=True, null=True, verbose_name="Факт. На фирма:")
    paid = models.CharField(max_length=80,  verbose_name="Платено", choices = (
        ('No', 'НЕ'),
        ('Yes', 'ДА'),
    ), default = 'No')
    cashdesk_fk = models.ForeignKey('cashdesk.Cashdesk', blank=True, null=True, verbose_name="Платено в каса")
    notes = models.TextField(max_length=2000, blank=True,null=True, verbose_name="Забележка")
    club_fk = models.ForeignKey('nomenclature.Club', verbose_name="Клуб")
    last_update_date = models.DateTimeField(blank=True, null=True, verbose_name="Дата на опресняване")

    # Computes dynamically total price of delivery, based on all detail models
    @property
    def delivery_amount(self):
        result = DeliveryDetail.objects.filter(delivery_fk=self).aggregate(amount=Sum(F('price')*F('cnt')))
        return nvl(result['amount'], 0)
    delivery_amount.fget.short_description = 'Крайна цена'

    def is_closed(self):
        if self.status in ('DELIVERED', 'CANCELED') or self.paid == 'Yes':
            return True
        return False

    class Meta:
            managed = True
            db_table = 'delivery'
            verbose_name = u"Доставка"
            verbose_name_plural = u"Доставки"

    def __str__(self):
        return str(self.supplier_fk) + ":" + str(self.delivery_date) + ":" + str(self.invoice_no) + " :" + str(self.delivery_amount) + " лв."


class DeliveryDetail(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="Номер")
    delivery_fk = models.ForeignKey('Delivery', null=True, verbose_name="Доставка N", )
    article_fk = models.ForeignKey('ArticleDelivery', blank=False, null=True, verbose_name="Артикул")
    cnt = models.DecimalField(max_digits=8, decimal_places=3, verbose_name="Количество", validators=[MinValueValidator(Decimal('0.001'))])
    price = models.DecimalField( max_digits=8, decimal_places=2, verbose_name="Единична цена", validators=[MinValueValidator(Decimal('0.01'))])
    amount = models.DecimalField( max_digits=8, decimal_places=2, verbose_name="Цена",blank=True, null=False)

    # @property
    # def amount(self):
    #     return nvl(self.price,0)*nvl(self.cnt,0)
    # amount.fget.short_description = 'Крайна цена'

    class Meta:
        managed = True
        db_table = 'delivery_detail'
        verbose_name = u"Доставка описание"
        verbose_name_plural = u"Доставки описание"

    def __str__(self):
        return str(self.article_fk.group_fk) + ":" + str(self.article_fk) + ":" + str(self.cnt) + " :" + str(self.price) + " лв."


class ArticleDeliveryManager(models.Manager):
    def get_queryset(self):
        return super(ArticleDeliveryManager, self).get_queryset().filter(active=True, delivery_price__gte=0)


class ArticleDelivery(Article):
    objects = ArticleDeliveryManager()

    class Meta:
        proxy = True
        verbose_name = u"Артикул доставки"
        verbose_name_plural = u"Артикули доставки"
