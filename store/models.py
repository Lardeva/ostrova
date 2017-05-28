from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class ArticleStore(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="Номер")
    create_date = models.DateTimeField(default=timezone.now, verbose_name="Дата на създаване")
    last_update_date = models.DateTimeField(blank=True, null=True, verbose_name="Дата на промяна")
    user = models.ForeignKey(User, blank=True, null=True, verbose_name="Служител")
    club_fk = models.ForeignKey('nomenclature.Club', null=True, verbose_name="Клуб")
    article_fk = models.ForeignKey('nomenclature.Article', blank=False, null=True, verbose_name="Артикул")
    cnt = models.DecimalField( max_digits=8, decimal_places=3, blank=True, null=True, verbose_name="Налично кол.")
    cnt_min = models.DecimalField( max_digits=8, decimal_places=3, blank=True, null=True, verbose_name="Минимално кол.")
    cnt_bl = models.DecimalField( max_digits=8, decimal_places=3, blank=True, null=True, verbose_name="Блокирано кол.")
    note = models.TextField(max_length=1000, blank=True, verbose_name="Забележка за блокировката")

    def __str__(self):
        return self.article_fk.group_fk.name + ":" + self.article_fk.name + ':' + str(self.cnt)

    class Meta:
        managed = True
        db_table = 'article_store'
        verbose_name = u"Складова наличност"
        verbose_name_plural = u"Складови наличности"


class stock_acceptance_detail(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="Номер")
    stock_protocol_fk = models.ForeignKey('store.Stock_receipt_protocol', verbose_name="Протокол")
    article_store_fk = models.ForeignKey('store.ArticleStore', blank=False, null=False, verbose_name="Артикул")
    deliverydetail_fk = models.ForeignKey('delivery.DeliveryDetail', blank=True, null=True, verbose_name="Доставено кол.")
    cnt = models.DecimalField( max_digits=8, decimal_places=3, verbose_name="Количество")

    class Meta:
        managed = True
        db_table = 'stock_acceptance_detail'
        verbose_name = u"Приемане на стока"
        verbose_name_plural = u"Приемане на стоки"

    def __str__(self):
        return str(self.article_store_fk.article_fk.name) + ":Приемане на стока:" + str(self.cnt) + ":" + str(self.deliverydetail_fk)


class stock_delivery_detail(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="Номер")
    stock_protocol_fk = models.ForeignKey('store.Stock_receipt_protocol', verbose_name="Протокол")
    article_store_fk = models.ForeignKey('store.ArticleStore', blank=False, null=False, verbose_name="Артикул")
    orderdetail_fk = models.ForeignKey('order.Orderdetail', blank=True, null=True, verbose_name="Поръчка детайл")
    cnt = models.DecimalField( max_digits=8, decimal_places=3, verbose_name="Количество")

    class Meta:
        managed = True
        db_table = 'stock_delivery_detail'
        verbose_name = u"Издаване на стока"
        verbose_name_plural = u"Издаване на стоки"

    def __str__(self):
        return str(self.article_store_fk.article_fk.name) + ":Издаване на стока:" + str(self.cnt) + ":" + str(self.orderdetail_fk)


class stock_receipt_protocol(models.Model):
    TYPES = (
        ('REVISION', 'ППП Ревизия'),
        ('ORDER', 'ППП Продажба'),
        ('DELIVERY', 'ППП Доставка'),
        ('EXPDELIVERY', 'ППП Доставка чрез експедиция'),
        ('CORDELIVERY', 'ППП Корекция доставка'),
        ('EXPEDITION', 'ППП Експедиция'),
        ('LATEORD', 'ППП Късно изписване'),
        ('INTERNAL', 'ППП Вътрешни нужди'),
        ('SCRAP', 'ППП Брак'),
    )

    MANUAL_TYPES = (
        ('REVISION', 'ППП Ревизия'),
        ('CORDELIVERY', 'ППП Корекция доставка'),
        ('EXPEDITION', 'ППП Експедиция'),
        ('LATEORD', 'ППП Късно изписване'),
        ('INTERNAL', 'ППП Вътрешни нужди'),
        ('SCRAP', 'ППП Брак'),
    )

    id = models.AutoField(primary_key=True, verbose_name="Номер")
    club_fk = models.ForeignKey('nomenclature.Club', verbose_name="Обект")
    order_fk = models.ForeignKey('order.Order', blank=True, null=True, verbose_name="Поръчка")
    delivery_fk = models.ForeignKey('delivery.Delivery', blank=True, null=True, verbose_name="Доставка")
    receipt_date = models.DateField(blank=True, null=True,verbose_name="Дата", default=timezone.now)
    type = models.CharField(max_length=40, verbose_name="Тип на протокола",choices=TYPES, default='REVISION', )
    closed = models.BooleanField(default=False, verbose_name="Приключен")
    transfer_fk = models.ForeignKey('store.Stock_receipt_protocol', blank=True, null=True, verbose_name="Трансфер")
    transfer_club_fk = models.ForeignKey('nomenclature.Club',blank=True, null=True, verbose_name="Към обект", related_name='stock_receipt_protocol_transfer_set')
    note = models.TextField(max_length=2000, blank=True, null=True, verbose_name="Забележка")

    class Meta:
        managed = True
        db_table = 'stock_receipt_protocol'
        verbose_name = u"Приемо Предавателен Протокол"
        verbose_name_plural = u"Приемо Предавателни Протоколи"

    def __str__(self):
        return str(self.club_fk) + ":" + str(dict(self.TYPES)[self.type])
