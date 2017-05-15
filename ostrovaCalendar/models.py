from decimal import Decimal
from django.utils import timezone
from django.db import models
from django.db.models import F
from django.db.models import Sum
from django.contrib.auth.models import User
from ostrovaweb.utils import nvl, AdminURLMixin


class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    club_fk = models.ForeignKey('Club', null=True, blank=True, verbose_name="Клуб")

    class Meta:
        managed = True
        db_table = 'Employee'
        verbose_name = u"Служител"
        verbose_name_plural = u"Служители"


class Supplier(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="Номер")
    name = models.CharField(max_length=60, blank=True, verbose_name="Име")
    description = models.CharField(max_length=500, blank=True, verbose_name="Описание")

    def __str__(self):
        return self.name

    class Meta:
        managed = True
        db_table = 'supplier'
        verbose_name = u"Доставчик"
        verbose_name_plural = u"Доставчици"


class Delivery(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="Номер")
    order_date = models.DateField( verbose_name="Дата на заявка", default=timezone.now)
    supplier_fk = models.ForeignKey('Supplier', verbose_name="Доставчик")
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
    cashdesk_fk = models.ForeignKey('Cashdesk',blank=True, null=True, verbose_name="Платено в каса")
    notes = models.TextField(max_length=2000, blank=True,null=True, verbose_name="Забележка")
    club_fk = models.ForeignKey('Club', verbose_name="Клуб")
    last_update_date = models.DateTimeField(blank=True, null=True, verbose_name="Дата на опресняване")

    # Computes dynamically total price of delivery, based on all detail models
    @property
    def delivery_amount(self):
        result = DeliveryDetail.objects.filter(delivery_fk=self).aggregate(amount=Sum(F('amount')))
        return nvl(result['amount'],0)
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

    def __str__( self ):
        return "Доставка N:" + str(self.id) + " / " + str(self.delivery_date) + " / " + str(self.invoice_no)+ " / " + str(self.supplier_fk)


class DeliveryDetail(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="Номер")
    delivery_fk = models.ForeignKey('Delivery', null=True, verbose_name="Доставка N", )
    article_fk = models.ForeignKey('ArticleDelivery', blank=False, null=True, verbose_name="Артикул")
    cnt = models.DecimalField(max_digits=8, decimal_places=3, verbose_name="Количество")
    price = models.DecimalField( max_digits=8, decimal_places=2, verbose_name="Единична цена")
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


class ArticleGroup(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="Номер")
    name = models.CharField(max_length=80, blank=False, null=False, verbose_name="Име")
    delivery_type = models.BooleanField(default=False, verbose_name="За доставки")
    order_type = models.BooleanField(default=False, verbose_name="За продажби")
    create_date = models.DateTimeField(blank=True, null=True, verbose_name="Дата на създаване")
    
    def __str__(self):
        return self.name

    class Meta:
        managed = True
        db_table = 'article_group'
        verbose_name = u"Артикулна група"
        verbose_name_plural = u"Артикулни групи"


class Article(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="Номер")
    name = models.CharField(max_length=100, blank=True, verbose_name="Име")
    group_fk = models.ForeignKey('ArticleGroup', null=True, verbose_name="Артикулна група")
    description = models.TextField(max_length=2000, blank=True, verbose_name="Описание")
    supplier_fk = models.ManyToManyField('Supplier', verbose_name="Доставчик")
    delivery_price = models.DecimalField( max_digits=8, decimal_places=2, blank=True, null=True, verbose_name="Доставна цена")
    sale_price = models.DecimalField( max_digits=8, decimal_places=2, blank=True, null=True, verbose_name="Продажна цена")
    last_price_dl = models.DecimalField( max_digits=8, decimal_places=2, blank=True, null=True, verbose_name="Посл.Цена на доставка")
    last_price_sl = models.DecimalField( max_digits=8, decimal_places=2, blank=True, null=True, verbose_name="Посл.Цена на продажба")
    last_update_date = models.DateTimeField(blank=True, null=True, verbose_name="Дата промяна")
    measure = models.CharField(max_length=50, blank=True, null=True, verbose_name="Мярка")
    active = models.BooleanField(default=True, verbose_name="Активен",)


    def __str__(self):

        return self.group_fk.name + ":" + self.name

    class Meta:
        managed = True
        db_table = 'article'
        verbose_name = u"Артикул"
        verbose_name_plural = u"Артикули"

class ArticleOrderManager(models.Manager):
    def get_queryset(self):
        return super(ArticleOrderManager, self).get_queryset().filter(active =True, sale_price__gte=0)

class ArticleOrder(Article):
    objects = ArticleOrderManager()
    class Meta:
        proxy = True
        verbose_name = u"Артикул продажби"
        verbose_name_plural = u"Артикули продажби"

class ArticleDeliveryManager(models.Manager):
    def get_queryset(self):
        return super(ArticleDeliveryManager, self).get_queryset().filter(active =True, delivery_price__gte=0)

class ArticleDelivery(Article):
    objects = ArticleDeliveryManager()
    class Meta:
        proxy = True
        verbose_name = u"Артикул доставки"
        verbose_name_plural = u"Артикули доставки"
class ArticleStore(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="Номер")
    create_date = models.DateTimeField(default=timezone.now, verbose_name="Дата на създаване")
    last_update_date = models.DateTimeField(blank=True, null=True, verbose_name="Дата на промяна")
    user = models.ForeignKey(User, verbose_name="Служител")
    club_fk = models.ForeignKey('Club', null=True, verbose_name="Клуб")
    article_fk = models.ForeignKey('Article', blank=False, null=True, verbose_name="Артикул")
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

class Club(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="Номер")
    name = models.CharField(max_length=240, blank=True, verbose_name='Име')
    hall_price = models.DecimalField( max_digits=8, decimal_places=2, blank=True, null=True, verbose_name='Цена на зала')
    address = models.CharField(max_length=240, blank=True, verbose_name='Адрес')

    def __str__(self):
        return self.name

    class Meta:
        managed = True
        db_table = 'club'
        verbose_name = u"Клуб"
        verbose_name_plural = u"Клубове"


class Saloon(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="Номер")
    club_fk = models.ForeignKey('Club', null=True, verbose_name="Клуб")
    name = models.CharField(max_length=200, blank=True,  verbose_name="Име")

    def __str__(self):
        return self.club_fk.name + ":" + self.name

    class Meta:
        db_table = 'saloon'
        verbose_name = u"Салон"
        verbose_name_plural = u"Салони"


class Order(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="Номер")
    rec_date = models.DateField(blank=True, null=True, verbose_name="Дата на р.д.")
    rec_time = models.CharField(max_length=80, blank=True, verbose_name="Начало")
    rec_time_end = models.CharField(max_length=40, blank=True, verbose_name="Край")
    phone = models.CharField(max_length=100, blank=True, verbose_name="Телефон")
    parent = models.CharField(max_length=240, blank=True, verbose_name="Родител")
    child = models.CharField(max_length=200, blank=True, verbose_name="Дете")
    age = models.IntegerField(blank=True, null=True, verbose_name="Години")
    child_count = models.IntegerField(blank=True, null=True, verbose_name="Брой деца")
    adult_count = models.IntegerField(blank=True, null=True, verbose_name="Брой възрастни")
    saloon_fk = models.ForeignKey('Saloon', verbose_name="Салон за възрастни")
    hall_count = models.IntegerField(blank=True, null=True, verbose_name="Брой зала")
    hall_price = models.DecimalField( max_digits=8, decimal_places=2, blank=True, null=True, verbose_name="Цена на зала")
    deposit = models.DecimalField( max_digits=8, decimal_places=2,blank=True, null=True, verbose_name="Капаро")
    discount = models.DecimalField( max_digits=8, decimal_places=2, blank=True, null=True, verbose_name="Отстъпка")
    price_final = models.DecimalField( max_digits=8, decimal_places=2, blank=True, null=True, verbose_name="Крайна цена")
    deposit_date = models.DateField(blank=True, null=True, verbose_name="Дата на капаро")
    payment_date = models.DateField(blank=True, null=True, verbose_name="Дата на плащане")
    validity_date = models.DateField(blank=True, null=True, verbose_name="Дата на валидност")
    refusal_date = models.DateField(blank=True, null=True, verbose_name="Дата на отказ")
    refusal_reason = models.CharField(max_length=400, blank=True, verbose_name="Причина за отказ")
    order_date = models.DateField(blank=True, null=True, verbose_name="Дата на поръчка")
    notes = models.TextField(max_length=12000, blank=True, verbose_name="Забележка")
    address = models.CharField(max_length=1024, blank=True, verbose_name="Адрес")
    user = models.ForeignKey(User, verbose_name="Служител")
    email = models.CharField(max_length=400, blank=True, verbose_name="E-mail")
    club_fk = models.ForeignKey('Club', null=True, verbose_name="Клуб")
    create_date = models.DateTimeField(default=timezone.now, verbose_name="Дата на създаване")
    last_update_date = models.DateTimeField(blank=True, null=True, verbose_name="Дата на промяна")
    changes = models.TextField(max_length=12000, blank=True, verbose_name="Промени")
    deposit2 = models.DecimalField( max_digits=8, decimal_places=2, blank=True, null=True, verbose_name="Капаро 2")
    deposit2_date = models.DateField(blank=True, null=True, verbose_name="Дата на капаро2")
    update_state = models.CharField(max_length=80, blank=True, verbose_name="Актуализация на състоянието")
    locked = models.BooleanField(default=False, max_length=4,  verbose_name="Приключено")
    payed_final = models.DecimalField( max_digits=8, decimal_places=2, blank=True, null=True, verbose_name="Финално плащане")
    notes_torta = models.TextField(max_length=2000, blank=True, verbose_name="Забележка за тортата")
    notes_kitchen = models.TextField(max_length=2000, blank=True, verbose_name="Забележка за кухнята")
    store_status = models.BooleanField(default=False, verbose_name=" Изписано от склада")
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
    cnt = models.DecimalField( max_digits=8, decimal_places=3, blank=True, null=True, verbose_name="Количество")
    price = models.DecimalField( max_digits=8, decimal_places=2, blank=True, null=True, verbose_name="Единична цена")

    def __str__( self ):
        return self.article_fk.group_fk.name + ":" + self.article_fk.name + ":" + str(self.cnt) + " " + self.article_fk.measure + " :" + str(self.price) + " лв."

    class Meta:
        managed = True
        db_table = 'order_detail'
        verbose_name = u"Поръчка описание"
        verbose_name_plural = u"Поръчки описание"


class Times(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="Номер")
    time_slot = models.IntegerField(blank=True, null=True,verbose_name="Часови сегмент")
    time = models.CharField(max_length=40, blank=True,verbose_name="Начало")
    time_end = models.CharField(max_length=40, blank=True,verbose_name="Край")
    weekday = models.IntegerField(blank=True, null=True,verbose_name="Ден от седмицата")

    def __str__(self):
        return self.time + ":" + self.time_end


    class Meta:
        managed = True
        db_table = 'times'
        verbose_name = u"Час"
        verbose_name_plural = u"Часове"


class Schedule(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="Номер")
    times_fk = models.ForeignKey('Times', verbose_name="Часови сегмент")
    order_fk = models.ForeignKey('Order', blank=True, null=True, verbose_name="Поръчка N")
    schedule_date = models.DateField(max_length=40, blank=True, verbose_name="Дата")
    club_fk = models.ForeignKey('Club', null=True, verbose_name="Клуб")

    def __str__(self):
        return str(self.schedule_date) + ":" + str(self.order_fk) + ":" + self.times_fk.time

    class Meta:
        managed = True
        db_table = 'schedule'
        verbose_name = u"Календар"
        verbose_name_plural = u"Календари"


class Cashdesk_groups_income(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="Номер")
    name = models.CharField(max_length=80, blank=True, verbose_name="Група")
    sub_name = models.CharField(max_length=120, blank=True, verbose_name="Подгрупа")

    def __str__( self ):
        return  self.name + ":" + self.sub_name

    class Meta:
        managed = True
        db_table = 'cashdesk_groups_income'
        verbose_name = u"Група каса приход"
        verbose_name_plural = u"Групи каса приход"


class Cashdesk_groups_expense(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="Номер")
    name = models.CharField(max_length=80, blank=True, verbose_name="Група")
    sub_name = models.CharField(max_length=120, blank=True, verbose_name="Подгрупа")

    def __str__( self ):
        return  self.name + ":" + self.sub_name

    class Meta:
        managed = True
        db_table = 'cashdesk_groups_expense'
        verbose_name = u"Група каса разход"
        verbose_name_plural = u"Групи каса разход"


class Cashdesk(AdminURLMixin, models.Model):
    id = models.AutoField(primary_key=True, verbose_name="Номер")
    rec_date = models.DateField(blank=True, null=True,verbose_name="Дата")
    beg_bank_100 = models.DecimalField( max_digits=8, decimal_places=0, blank=True, null=True, verbose_name="Банкноти по 100")
    beg_bank_50 = models.DecimalField( max_digits=8, decimal_places=0, blank=True, null=True, verbose_name="Банкноти по 50")
    beg_bank_20 = models.DecimalField( max_digits=8, decimal_places=0, blank=True, null=True, verbose_name="Банкноти по 20")
    beg_bank_10 = models.DecimalField( max_digits=8, decimal_places=0, blank=True, null=True, verbose_name="Банкноти по 10")
    beg_bank_5 = models.DecimalField( max_digits=8, decimal_places=0, blank=True, null=True, verbose_name="Банкноти по 5")
    beg_bank_2 = models.DecimalField( max_digits=8, decimal_places=0, blank=True, null=True, verbose_name="Банкноти по 2")
    beg_coin_100 = models.DecimalField( max_digits=8, decimal_places=0, blank=True, null=True, verbose_name="Стотинки по 100")
    beg_coin_50 = models.DecimalField( max_digits=8, decimal_places=0, blank=True, null=True, verbose_name="Стотинки по 50")
    beg_coin_20 = models.DecimalField( max_digits=8, decimal_places=0,  blank=True, null=True, verbose_name="Стотинки по 20")
    beg_coin_10 = models.DecimalField( max_digits=8, decimal_places=0,blank=True, null=True, verbose_name="Стотинки по 10")
    beg_coin_5 = models.DecimalField( max_digits=8, decimal_places=0, blank=True, null=True, verbose_name="Стотинки по 5")
    beg_close = models.ForeignKey(User, blank=True, null=True,related_name='beg_close', verbose_name="Предал")
    beg_open = models.ForeignKey(User, blank=True, null=True, related_name='beg_open', verbose_name="Приел")
    beg_close_date = models.DateField(blank=True, null=True, verbose_name="Дата на предаване")
    beg_open_date = models.DateField(blank=True, null=True, verbose_name="Дата на приемане")
    end_bank_100 =models.DecimalField( max_digits=8, decimal_places=0, blank=True, null=True, verbose_name="Банкноти по 100")
    end_bank_50 = models.DecimalField( max_digits=8, decimal_places=0, blank=True, null=True, verbose_name="Банкноти по 50")
    end_bank_20 = models.DecimalField( max_digits=8, decimal_places=0, blank=True, null=True, verbose_name="Банкноти по 20")
    end_bank_10 = models.DecimalField( max_digits=8, decimal_places=0, blank=True, null=True, verbose_name="Банкноти по 10")
    end_bank_5 = models.DecimalField( max_digits=8, decimal_places=0, blank=True, null=True, verbose_name="Банкноти по 5")
    end_bank_2 = models.DecimalField( max_digits=8, decimal_places=0, blank=True, null=True, verbose_name="Банкноти по 2")
    end_coin_100 = models.DecimalField( max_digits=8, decimal_places=0, blank=True, null=True, verbose_name="Стотинки по 100")
    end_coin_50 = models.DecimalField( max_digits=8, decimal_places=0, blank=True, null=True, verbose_name="Стотинки по 50")
    end_coin_20 = models.DecimalField( max_digits=8, decimal_places=0, blank=True, null=True, verbose_name="Стотинки по 20")
    end_coin_10 = models.DecimalField( max_digits=8, decimal_places=0, blank=True, null=True, verbose_name="Стотинки по 10")
    end_coin_5 = models.DecimalField( max_digits=8, decimal_places=0, blank=True, null=True, verbose_name=" Стотинки по 5")
    club_fk = models.ForeignKey('Club', null=True, verbose_name="Обект")
    create_date = models.DateTimeField(blank=True, null=True, verbose_name="Дата на създавне")
    last_update_date = models.DateTimeField(blank=True, null=True,verbose_name="Дата на промяна")
    status = models.CharField(max_length=80, verbose_name="Статус", choices = (
        ('OPENED', 'ОТВОРЕНА'),
        ('JUSTCLOSED', 'ПОСЛЕДНО ЗАТВОРЕНА'),
        ('CLOSED', 'ЗАТВОРЕНА'),
       ), default='OPENED')

    @property
    def beg_amount(self):
        return round(nvl(self.beg_coin_5,0) * Decimal(0.05) +
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
        return round(nvl(self.end_coin_5,0) * Decimal(0.05) +
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
    order_fk = models.ForeignKey('Order', blank=True, null=True, verbose_name="Плащане по поръчка")
    group_fk = models.ForeignKey('Cashdesk_groups_income', verbose_name="Група приходи")
    note = models.CharField(max_length=400, blank=True, null=True, verbose_name="Забележка")
    amount = models.DecimalField( max_digits=8, decimal_places=2, verbose_name="Сума")
    transfer_fk = models.ForeignKey('Cashdesk_detail_expense', blank=True, null=True, verbose_name="Трансфер")
    transfer_club_fk = models.ForeignKey('Club',blank=True, null=True, verbose_name="Към обект", related_name='cashdesk_detail_income_transfer_set')

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
    delivery_fk = models.ForeignKey('Delivery', blank=True, null=True, verbose_name="Плащане по доставка")
    group_fk = models.ForeignKey('Cashdesk_groups_expense', verbose_name="Група разходи")
    note = models.CharField(max_length=400, blank=True, null=True, verbose_name="Забележка")
    amount = models.DecimalField( max_digits=8, decimal_places=2, verbose_name="Сума")
    transfer_fk = models.ForeignKey('Cashdesk_detail_income', blank=True, null=True, verbose_name="Трансфер")
    transfer_club_fk = models.ForeignKey('Club',blank=True, null=True, verbose_name="Към обект", related_name='cashdesk_detail_expense_transfer_set')

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

class stock_acceptance_detail(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="Номер")
    stock_protocol_fk = models.ForeignKey('Stock_receipt_protocol', verbose_name="Протокол")
    article_store_fk = models.ForeignKey('ArticleStore', blank=False, null=False, verbose_name="Артикул")
    deliverydetail_fk = models.ForeignKey('DeliveryDetail', blank=True, null=True, verbose_name="Доставено кол.")
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
    stock_protocol_fk = models.ForeignKey('Stock_receipt_protocol', verbose_name="Протокол")
    article_store_fk = models.ForeignKey('ArticleStore', blank=False, null=False, verbose_name="Артикул")
    orderdetail_fk = models.ForeignKey('Orderdetail', blank=True, null=True, verbose_name="Поръчка детайл")
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
    club_fk = models.ForeignKey('Club', verbose_name="Обект")
    order_fk = models.ForeignKey('Order', blank=True, null=True, verbose_name="Поръчка")
    delivery_fk = models.ForeignKey('Delivery', blank=True, null=True, verbose_name="Доставка")
    receipt_date = models.DateField(blank=True, null=True,verbose_name="Дата", default=timezone.now)
    type = models.CharField(max_length=40, verbose_name="Тип на протокола",choices=TYPES, default='REVISION', )
    closed = models.BooleanField(default=False, verbose_name="Приключен")
    transfer_fk = models.ForeignKey('Stock_receipt_protocol', blank=True, null=True, verbose_name="Трансфер")
    transfer_club_fk = models.ForeignKey('Club',blank=True, null=True, verbose_name="Към обект", related_name='stock_receipt_protocol_transfer_set')
    note = models.TextField(max_length=2000, blank=True, null=True, verbose_name="Забележка")

    class Meta:
        managed = True
        db_table = 'stock_receipt_protocol'
        verbose_name = u"Приемо Предавателен Протокол"
        verbose_name_plural = u"Приемо Предавателни Протоколи"

    def __str__(self):
        return str(self.club_fk) + ":" + str(dict(self.TYPES)[self.type])