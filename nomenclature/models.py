from django.db import models
from django.contrib.auth.models import User


class Club(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="Номер")
    name = models.CharField(max_length=240, verbose_name='Име')
    hall_price = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True, verbose_name='Цена на зала')
    address = models.CharField(max_length=240, blank=True, null=True, verbose_name='Адрес')

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
    name = models.CharField(max_length=200, verbose_name="Име")
    default = models.BooleanField("Основен", default=False)

    def __str__(self):
        return self.club_fk.name + ":" + self.name

    class Meta:
        db_table = 'saloon'
        verbose_name = u"Салон"
        verbose_name_plural = u"Салони"


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
    name = models.CharField(max_length=60, verbose_name="Име")
    description = models.CharField(max_length=500, blank=True, null=True, verbose_name="Описание")

    def __str__(self):
        return self.name

    class Meta:
        managed = True
        db_table = 'supplier'
        verbose_name = u"Доставчик"
        verbose_name_plural = u"Доставчици"


class ArticleGroup(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="Номер")
    name = models.CharField(max_length=80, verbose_name="Име")
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
    name = models.CharField(max_length=100, verbose_name="Име")
    group_fk = models.ForeignKey('ArticleGroup', null=True, verbose_name="Артикулна група")
    description = models.TextField(max_length=2000, blank=True, null=True, verbose_name="Описание")
    supplier_fk = models.ManyToManyField('Supplier', verbose_name="Доставчик")
    delivery_price = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True, verbose_name="Доставна цена")
    sale_price = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True, verbose_name="Продажна цена")
    last_price_dl = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True, verbose_name="Посл.Цена на доставка")
    last_price_sl = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True, verbose_name="Посл.Цена на продажба")
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


class Cashdesk_groups_income(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="Номер")
    name = models.CharField(max_length=80, blank=True, verbose_name="Група")
    sub_name = models.CharField(max_length=120, blank=True, verbose_name="Подгрупа")

    def __str__(self):
        return self.name + ":" + self.sub_name

    class Meta:
        managed = True
        db_table = 'cashdesk_groups_income'
        verbose_name = u"Група каса приход"
        verbose_name_plural = u"Групи каса приход"


class Cashdesk_groups_expense(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="Номер")
    name = models.CharField(max_length=80, blank=True, verbose_name="Група")
    sub_name = models.CharField(max_length=120, blank=True, verbose_name="Подгрупа")

    def __str__(self):
        return self.name + ":" + self.sub_name

    class Meta:
        managed = True
        db_table = 'cashdesk_groups_expense'
        verbose_name = u"Група каса разход"
        verbose_name_plural = u"Групи каса разход"
