from datetime import datetime
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from reversion_compare.admin import CompareVersionAdmin

from cashdesk.models import Cashdesk
from nomenclature.models import *


class ClubAdmin(admin.ModelAdmin):
    fields = ('name', 'hall_price', 'address',)
    list_display =( 'name', 'hall_price', 'address',)

    def save_model(self, request, obj, form, change):
        if obj.id is None:
            obj.save()

            newCashdesk=Cashdesk()
            newCashdesk.rec_date =datetime.now()

            newCashdesk.beg_bank_100 = 0
            newCashdesk.beg_bank_50  = 0
            newCashdesk.beg_bank_20  = 0
            newCashdesk.beg_bank_10  = 0
            newCashdesk.beg_bank_5   = 0
            newCashdesk.beg_bank_2   = 0
            newCashdesk.beg_coin_100 = 0
            newCashdesk.beg_coin_50  = 0
            newCashdesk.beg_coin_20  = 0
            newCashdesk.beg_coin_10  = 0
            newCashdesk.beg_coin_5   = 0

            newCashdesk.beg_open = request.user
            newCashdesk.beg_open_date = datetime.now()
            newCashdesk.club_fk = obj
            newCashdesk.create_date = datetime.now()
            newCashdesk.last_update_date = datetime.now()
            newCashdesk.status = 'OPENED'
            newCashdesk.save()
        super(ClubAdmin,self).save_model(request, obj, form, change)

admin.site.register(Club, ClubAdmin)


class SaloonAdmin(CompareVersionAdmin):
    fields = ('club_fk', 'name')

admin.site.register(Saloon, SaloonAdmin)


class SupplierAdmin(admin.ModelAdmin):
    fields = ('name',)
admin.site.register(Supplier, SupplierAdmin)


class ArticleGroupAdmin(admin.ModelAdmin):
    fields = ('name','delivery_type','order_type','create_date',)
    list_display =('name','delivery_type','order_type',)
    #   list_editable = ('delivery_type','order_type',)
    readonly_fields = ('create_date',)

admin.site.register(ArticleGroup, ArticleGroupAdmin)


class ArticleAdmin(admin.ModelAdmin):
    fields = ('id','name', 'description','measure','last_update_date','group_fk','supplier_fk','delivery_price','sale_price','active',)
    list_display =('name','group_fk','description','measure','delivery_price','sale_price','active',)
    readonly_fields = ('last_update_date','id',)

    filter_horizontal = ('supplier_fk',)

    list_filter = ('group_fk','active')
    search_fields = ('name', 'description')

admin.site.register(Article, ArticleAdmin)


class Cashdesk_groups_incomeAdmin(admin.ModelAdmin):
    fields = ('name', 'sub_name',)
    list_display = ('name', 'sub_name',)

admin.site.register(Cashdesk_groups_income, Cashdesk_groups_incomeAdmin)


class Cashdesk_Groups__expenseAdmin(admin.ModelAdmin):
    fields = ('name', 'sub_name',)
    list_display = ('name', 'sub_name',)

admin.site.register(Cashdesk_groups_expense, Cashdesk_Groups__expenseAdmin)


# Define an inline admin descriptor for Employee model
# which acts a bit like a singleton
class EmployeeInline(admin.StackedInline):
    model = Employee
    can_delete = False
    verbose_name_plural = 'Допълнителни данни за служител'

# Define a new User admin
class EmployeeAdmin(UserAdmin):
    inlines = (EmployeeInline, )

    def save_model(self, request, obj, form, change):
        if not hasattr(obj, 'employee'):
            obj.save()

            emp = Employee()
            emp.user = obj
            emp.save()

            obj.employee = emp

        super(EmployeeAdmin, self).save_model(request, obj, form, change)

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, EmployeeAdmin)