from datetime import datetime
from django.db import models
from django.db.models import Sum
from django.utils import timezone
# from django_permanent.models import PermanentModel
from django.contrib.auth.models import User
from datetime import datetime
# Create your models here.
from ostrovaweb.utils import nvl, AdminURLMixin


class Supplier(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="Номер")
    name = models.CharField(max_length=60, blank=True, verbose_name="Име")
    description = models.CharField(max_length=500, blank=True, verbose_name="Описание")

    def __str__( self ):
        return  self.name


    class Meta:
        managed = True
        db_table = 'supplier'
        verbose_name = u"Доставчик"
        verbose_name_plural = u"Доставчици"

class Delivery(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="Номер")
    order_date = models.DateField(blank=True, null=True, verbose_name="Дата на заявка")
    supplier_fk = models.ForeignKey('Supplier', blank=True, null=True, verbose_name="Доставчик")
    status = models.CharField(max_length=80, blank=True, verbose_name="Статус", choices = (
        ('ПОРЪЧАНO', 'ПОРЪЧАНO'),
        ('ДОСТАВЕНО', 'ДОСТАВЕНО'),
        ('ОТКАЗАНО', 'ОТКАЗАНО'),
    ))
    user = models.ForeignKey(User, verbose_name="Служител")
    delivery_date = models.DateField(blank=True, null=True, verbose_name="Дата на доставка ")
    invoice_no = models.CharField(max_length=400, blank=True, verbose_name="Номер на фактура")
    firm_invoice_no = models.CharField(max_length=400, blank=True, verbose_name="Факт. На фирма:")
    paid = models.CharField(max_length=80, blank=True, verbose_name="Платено", choices = (
        ('ДА', 'ДА'),
        ('НЕ', 'НЕ'),
    ))
    cashdesk_fk = models.ForeignKey('Cashdesk',blank=True, null=True, verbose_name="Дата на плащане")
    notes = models.TextField(max_length=2000, blank=True, verbose_name="Забележка")
    club_fk = models.ForeignKey('Club', null=True, verbose_name="Клуб")
    delivery_amount = models.FloatField(blank=True, null=True, verbose_name="Крайна цена")
    last_update_date = models.DateTimeField(blank=True, null=True, verbose_name="Дата на опресняване")
    class Meta:
        managed = True
        db_table = 'delivery'
        verbose_name = u"Доставка"
        verbose_name_plural = u"Доставки"

    def __str__( self ):
        return str(self.supplier_fk) + ":" + str(self.delivery_date) + ":" + str(self.invoice_no)+ " :" + str(self.delivery_amount) + " лв."

    #suit_form_tabs = (('provider', 'Provider'), ('information', 'Information'),('notes', 'Notes'))

class DeliveryDetail(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="Номер")
    delivery_fk = models.ForeignKey('Delivery', null=True, verbose_name="Доставка N", )
    group_fk = models.ForeignKey('ArticleGroup', blank=False, null=True, verbose_name="Артикулна група")
    article_fk = models.ForeignKey('Article', blank=False, null=True, verbose_name="Артикул")
    cnt = models.FloatField(blank=True, null=True, verbose_name="Количество")
    price = models.FloatField(blank=True, null=True, verbose_name="Единична цена")
    price_actual = models.FloatField(blank=True, null=True, verbose_name="Цена")
    goods_id = models.IntegerField(blank=True, null=True, verbose_name="Номер на стока")
    class Meta:
        managed = True
        db_table = 'delivery_detail'
        verbose_name = u"Доставка описание"
        verbose_name_plural = u"Доставки описание"


class ArticleGroup(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="Номер")
    name = models.CharField(max_length=80, blank=False, null=False, verbose_name="Име")
    delivery_type = models.BooleanField(default=False, verbose_name="За доставки")
    order_type = models.BooleanField(default=False, verbose_name="За продажби")
    create_date = models.DateTimeField(blank=True, null=True, verbose_name="Дата на създаване")
    
    def __str__( self ):
        return  self.name

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
    delivery_price = models.FloatField(blank=True, null=True, verbose_name="Доставна цена")
    sale_price = models.FloatField(blank=True, null=True, verbose_name="Продажна цена")
    last_price_dl = models.FloatField(blank=True, null=True, verbose_name="Посл.Цена на доставка")
    last_price_sl = models.FloatField(blank=True, null=True, verbose_name="Посл.Цена на продажба")
    last_update_date = models.DateTimeField(blank=True, null=True, verbose_name="Дата промяна")
    measure = models.CharField(max_length=50, blank=True, null=True, verbose_name="Мярка")
    active = models.BooleanField(default=True, verbose_name="Активен")
    def __str__( self ):
        return self.group_fk.name + ":"+ self.name


    class Meta:
        managed = True
        db_table = 'article'
        verbose_name = u"Артикул"
        verbose_name_plural = u"Артикули"


class Club(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="Номер")
    name = models.CharField(max_length=240, blank=True, verbose_name='Име')
    hall_price = models.FloatField(blank=True, null=True, verbose_name='Цена на зала')
    address = models.CharField(max_length=240, blank=True, verbose_name='Адрес')

    def __str__( self ):
        return self.name

    class Meta:
        managed = True
        db_table = 'club'
        verbose_name = u"Клуб"
        verbose_name_plural = u"Клубове"

class Saloon (models.Model):
    id = models.AutoField(primary_key=True, verbose_name="Номер")
    club_fk = models.ForeignKey('Club', null=True, verbose_name="Клуб")
    name = models.CharField(max_length=200, blank=True,  verbose_name="Име")

    def __str__( self ):
        return self.club_fk.name + ":" + self.name

    class Meta:
        db_table = 'saloon'
        verbose_name = u"Салон"
        verbose_name_plural = u"Салони"

class Order(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="Номер")
    rec_date = models.DateField(blank=True, null=True, verbose_name="Дата на р.д.")
    rec_time_slot = models.IntegerField(blank=True, null=True, verbose_name="Слот")
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
    hall_price = models.FloatField(blank=True, null=True, verbose_name="Цена на зала")
    deposit = models.FloatField(blank=True, null=True, verbose_name="Капаро")
    discount = models.FloatField(blank=True, null=True, verbose_name="Отстъпка")
    price_final = models.FloatField(blank=True, null=True, verbose_name="Крайна цена")
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
    create_date = models.DateTimeField(blank=True, null=True, verbose_name="Дата на създаване")
    last_update_date = models.DateTimeField(blank=True, null=True, verbose_name="Дата на промяна")
    changes = models.TextField(max_length=12000, blank=True, verbose_name="Промени")
    deposit2 = models.FloatField(blank=True, null=True, verbose_name="Капаро 2")
    deposit2_date = models.DateField(blank=True, null=True, verbose_name="Дата на капаро2")
    update_state = models.CharField(max_length=80, blank=True, verbose_name="Актуализация на състоянието")
    locked = models.CharField(max_length=4, blank=True, verbose_name="Статус за приключване")
    payed_final = models.FloatField(blank=True, null=True, verbose_name="Финално плащане")
    notes_torta = models.TextField(max_length=2000, blank=True, verbose_name="Забележка за тортата")
    notes_kitchen = models.TextField(max_length=2000, blank=True, verbose_name="Забележка за кухнята")

    def __str__( self ):
        return str(self.parent) + ":" + str(self.phone) + ":" + str(self.child)+ " :" + str(self.deposit) + " лв."

    class Meta:
        managed = True
        db_table = 'order'
        verbose_name = u"Поръчка"
        verbose_name_plural = u"Поръчки"

    #suit_form_tabs = (('club', 'Club'),('order', 'Order'), ('client', 'Client'),('paymends1', 'Paymends1'),('paymends2', 'Paymends2'),('notes', 'Notes'))


class OrderDetail(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="Номер")
    order_fk = models.ForeignKey('Order', null=True, verbose_name="Поръчка N")
    group_fk = models.ForeignKey('ArticleGroup', blank=False, null=False, verbose_name="Артикулна група")
    article_fk = models.ForeignKey('Article', blank=False, null=False, verbose_name="Артикул")
    cnt = models.FloatField(blank=True, null=True, verbose_name="Количество")
    price = models.FloatField(blank=True, null=True, verbose_name="Единична цена")
    # child_menu = models.CharField(max_length=400, blank=True, verbose_name="Меню деца")
    # child_menu_cnt = models.IntegerField( blank=True, null=True, verbose_name="Меню деца брой")
    # child_menu_prc = models.FloatField(blank=True, null=True,verbose_name="Меню деца цена")
    # dmenu_order_status = models.CharField(max_length=80, blank=True, verbose_name="Меню деца статус")
    # dmenu_order_id = models.IntegerField(blank=True, null=True, verbose_name="Номер Меню деца")
    # program_id = models.IntegerField(blank=True, null=True, verbose_name="Номер на програма")
    # program = models.CharField(max_length=240, blank=True, verbose_name="Програма")
    # program_price = models.FloatField(blank=True, null=True, verbose_name="Цена на програма")
    # dshamp_cnt = models.IntegerField(blank=True, null=True, verbose_name="Детско шампанско")
    # dshamp_price = models.FloatField(blank=True, null=True, verbose_name="Детско шампанско цена")


    def __str__( self ):
        return self.group_fk.name + ":" + self.article_fk.name + ":" + str(self.cnt) + " "+ self.article_fk.measure + " :" + str(self.price) + " лв."

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

    def __str__( self ):
        return  self.time + ":" + self.time_end


    class Meta:
        managed = True
        db_table = 'times'
        verbose_name = u"Час"
        verbose_name_plural = u"Часове"

class Schedule(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="Номер")
    times_fk =models.ForeignKey('Times', verbose_name="Часови сегмент" )
    order_fk = models.ForeignKey('Order', blank=True, null=True, verbose_name="Поръчка N")
    schedule_date =models.DateField(max_length=40, blank=True, verbose_name="Дата")
    club_fk = models.ForeignKey('Club', null=True, verbose_name="Клуб")

    def __str__(self):
        return  str(self.schedule_date) + ":"+ str(self.order_fk) + ":" + self.times_fk.time

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
    beg_bank_100 = models.IntegerField(blank=True, null=True, verbose_name="Банкноти по 100")
    beg_bank_50 = models.IntegerField(blank=True, null=True, verbose_name="Банкноти по 50")
    beg_bank_20 = models.IntegerField(blank=True, null=True, verbose_name="Банкноти по 20")
    beg_bank_10 = models.IntegerField(blank=True, null=True, verbose_name="Банкноти по 10")
    beg_bank_5 = models.IntegerField(blank=True, null=True, verbose_name="Банкноти по 5")
    beg_bank_2 = models.IntegerField(blank=True, null=True, verbose_name="Банкноти по 2")
    beg_coin_100 = models.IntegerField(blank=True, null=True, verbose_name="Стотинки по 100")
    beg_coin_50 = models.IntegerField(blank=True, null=True, verbose_name="Стотинки по 50")
    beg_coin_20 = models.IntegerField(blank=True, null=True, verbose_name="Стотинки по 20")
    beg_coin_10 = models.IntegerField(blank=True, null=True, verbose_name="Стотинки по 10")
    beg_coin_5 = models.IntegerField(blank=True, null=True, verbose_name="Стотинки по 5")
    beg_close = models.ForeignKey(User, blank=True, null=True,related_name='beg_close', verbose_name="Предал")
    beg_open = models.ForeignKey(User, blank=True, null=True, related_name='beg_open', verbose_name="Приел")
    beg_close_date = models.DateField(blank=True, null=True, verbose_name="Дата на предаване")
    beg_open_date = models.DateField(blank=True, null=True, verbose_name="Дата на приемане")
    end_bank_100 = models.IntegerField(blank=True, null=True, verbose_name="Банкноти по 100")
    end_bank_50 = models.IntegerField(blank=True, null=True, verbose_name="Банкноти по 50")
    end_bank_20 = models.IntegerField(blank=True, null=True, verbose_name="Банкноти по 20")
    end_bank_10 = models.IntegerField(blank=True, null=True, verbose_name="Банкноти по 10")
    end_bank_5 = models.IntegerField(blank=True, null=True, verbose_name="Банкноти по 5")
    end_bank_2 = models.IntegerField(blank=True, null=True, verbose_name="Банкноти по 2")
    end_coin_100 = models.IntegerField(blank=True, null=True, verbose_name="Стотинки по 100")
    end_coin_50 = models.IntegerField(blank=True, null=True, verbose_name="Стотинки по 50")
    end_coin_20 = models.IntegerField(blank=True, null=True, verbose_name="Стотинки по 20")
    end_coin_10 = models.IntegerField(blank=True, null=True, verbose_name="Стотинки по 10")
    end_coin_5 = models.IntegerField(blank=True, null=True, verbose_name="Стотинки по 5")
    club_fk = models.ForeignKey('Club', null=True, verbose_name="Обект")
    create_date = models.DateTimeField(blank=True, null=True, verbose_name="Дата на създавне")
    last_update_date = models.DateTimeField(blank=True, null=True,verbose_name="Дата на промяна")


    @property
    def beg_amount(self):
        return (nvl(self.beg_coin_5,0) * 0.05 +
                nvl(self.beg_coin_10,0) * 0.1 +
                nvl(self.beg_coin_20,0) * 0.2 +
                nvl(self.beg_coin_50,0) * 0.5 +
                nvl(self.beg_coin_100,0) * 1.0 +
                nvl(self.beg_bank_2,0) * 2 +
                nvl(self.beg_bank_5,0) * 5 +
                nvl(self.beg_bank_10,0) * 10.00 +
                nvl(self.beg_bank_20,0) * 20 +
                nvl(self.beg_bank_50,0) * 50 +
                nvl(self.beg_bank_100,0) * 100 )
    beg_amount.fget.short_description = 'Сума в началото на деня'

    @property
    def end_amount(self):
        return (nvl(self.end_coin_5,0) * 0.05 +
                nvl(self.end_coin_10,0) * 0.1 +
                nvl(self.end_coin_20,0) * 0.2 +
                nvl(self.end_coin_50,0) * 0.5 +
                nvl(self.end_coin_100,0) * 1.0 +
                nvl(self.end_bank_2,0) * 2 +
                nvl(self.end_bank_5,0) * 5 +
                nvl(self.end_bank_10,0) * 10.00 +
                nvl(self.end_bank_20,0) * 20 +
                nvl(self.end_bank_50,0) * 50 +
                nvl(self.end_bank_100,0) * 100 )
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

    def __str__( self ):
        return str(self.id) + ":" + str(self.club_fk)+ ":" + str(self.rec_date)


class Cashdesk_detail_income(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="Номер")
    cashdesk = models.ForeignKey('Cashdesk', verbose_name="Каса")
    delivery_fk = models.ForeignKey('Delivery', blank=True, null=True, verbose_name="Плащане по доставка")
    cashdesk_groups_income_fk = models.ForeignKey('Cashdesk_groups_income', null=True, verbose_name="Група каса приходи")
    name = models.CharField(max_length=400, blank=True, null=True, verbose_name="Забележка")
    amount = models.FloatField(verbose_name="Сума")
    # master_group = models.CharField(max_length=80, blank=True, verbose_name="Мастер Група")
    # master_sub_group = models.CharField(max_length=120, blank=True, verbose_name="Мастер Подгрупа")
    #
    class Meta:
        managed = True
        db_table = 'cashdesk_detail_income'
        verbose_name = u"Приходен касов ордер"
        verbose_name_plural = u"Приходни касови ордери"
        
class Cashdesk_detail_expense(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="Номер")
    cashdesk = models.ForeignKey('Cashdesk', verbose_name="Каса")
    order_fk = models.ForeignKey('Order', blank=True, null=True, verbose_name="Плащане по поръчка")
    cashdesk_groups_expense_fk = models.ForeignKey('Cashdesk_groups_expense', null=True, verbose_name="Групи каса разходи")
    name = models.CharField(max_length=400, blank=True, null=True, verbose_name="Забележка")
    amount = models.FloatField(verbose_name="Сума")
    # master_group = models.CharField(max_length=80, blank=True, verbose_name="Мастер Група")
    # master_sub_group = models.CharField(max_length=120, blank=True, verbose_name="Мастер Подгрупа")
    #
    class Meta:
        managed = True
        db_table = 'cashdesk_detail_expense'
        verbose_name = u"Разходен касов ордер"
        verbose_name_plural = u"Разходни касови ордери"


class Store(models.Model):
    id = models.AutoField( primary_key=True, verbose_name="Номер")
    club_fk = models.ForeignKey('Club', null=True, verbose_name="Клуб")
    article_fk = models.ForeignKey('Article', null=True, verbose_name="Артикул")
    name = models.CharField(max_length=400, blank=True, verbose_name="Име")
    cnt_del_fk = models.ForeignKey('DeliveryDetail', blank=True, null=True, verbose_name="дост.к-во")
    cnt_or_fk = models.ForeignKey('OrderDetail',blank=True, null=True, verbose_name="пор.к-во")
    # cnt = models.FloatField(blank=True, null=True, verbose_name="Налично кол.")
    # cnt = models.FloatField(blank=True, null=True, verbose_name="Брак")
    price_actual = models.FloatField(blank=True, null=True, verbose_name="Цена")
    order_date = models.DateField(blank=True, null=True, verbose_name="Дата на Поръчка")
    delivery_date = models.DateField(blank=True, null=True, verbose_name="Дата на доставка ")
    type = models.CharField(max_length=40, blank=True, verbose_name="Тип")

    def __str__( self ):
        return self.name

    class Meta:
        managed = True
        db_table = 'Store'
        verbose_name = u"Склад"
        verbose_name_plural = u"Складове"