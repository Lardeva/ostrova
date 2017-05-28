from datetime import datetime, timedelta

from adminextensions.list_display import related_field
from django.contrib import admin
from django.contrib import messages
from django.shortcuts import redirect
from django_object_actions import DjangoObjectActions
from reversion_compare.admin import CompareVersionAdmin

from cashdesk.models import *
from nomenclature.models import Cashdesk_groups_income


class Cashdesk_detail_incomeAdmin(admin.ModelAdmin):
    fields = ('cashdesk', 'group_fk', 'note','amount','order_fk')
    list_display =(related_field('cashdesk__rec_date', None, 'Дата'),'cashdesk', 'group_fk', 'note','amount',)
    readonly_fields = ('cashdesk', 'group_fk', 'note','amount','order_fk')
    list_filter = ('cashdesk__rec_date','cashdesk__club_fk','cashdesk', 'group_fk','note',)
    #search_fields = ('cashdesk', 'group_fk__name','group_fk__sub_name')
    list_per_page = 50
    #date_hierarchy = "('cashdesk__rec_date', None, 'Дата')"
    search_fields = ('note','group_fk__name','group_fk__sub_name')
    def has_delete_permission(self, request, obj=None):
        return False

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields

        return ('order_fk',)

admin.site.register(Cashdesk_detail_income, Cashdesk_detail_incomeAdmin)


class Cashdesk_detail_expenseAdmin(admin.ModelAdmin):
    fields = ('cashdesk', 'group_fk','note','amount','delivery_fk')
    list_display =(related_field('cashdesk__rec_date', None, 'Дата'),'cashdesk', 'get_club_name', 'group_fk', 'note','amount',)
    readonly_fields = ('cashdesk', 'group_fk','note','amount','delivery_fk')
    list_filter = ('cashdesk__rec_date','cashdesk__club_fk','cashdesk', 'group_fk',)
    search_fields = ('note','group_fk__name','group_fk__sub_name')
    list_per_page = 50
    # date_hierarchy = "rec_date"

    def get_queryset(self, request):
        qs = super(Cashdesk_detail_expenseAdmin, self).get_queryset(request)
        qs = qs.filter(cashdesk__status__in = ('OPENED','JUSTCLOSED',))
        if request.user.employee.club_fk is not None:
            qs.filter(cashdesk__club_fk = request.user.employee.club_fk)
        return qs

    def get_club_name(self, obj):
        return obj.cashdesk.club_fk.name
    get_club_name.short_description = 'Клуб'

    def has_delete_permission(self, request, obj=None):
        return False

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields

        return ('delivery_fk',)

admin.site.register(Cashdesk_detail_expense, Cashdesk_detail_expenseAdmin)


class Cashdesk_detail_transferAdmin(admin.ModelAdmin):
    fields = ('cashdesk', 'group_fk','note','amount','transfer_club_fk')
    list_display =(related_field('cashdesk__rec_date', None, 'Дата'),'cashdesk', 'get_club_name', 'group_fk', 'note','amount',)
    readonly_fields = ('cashdesk', 'group_fk','note','amount','transfer_club_fk')
    list_filter = ('cashdesk__rec_date','cashdesk', 'group_fk',)
    search_fields = ('note','group_fk__name','group_fk__sub_name')
    list_per_page = 50
    # date_hierarchy = "rec_date"

    def get_queryset(self, request):
        qs = super(Cashdesk_detail_transferAdmin, self).get_queryset(request)
        qs = qs.filter(cashdesk__status__in = ('OPENED','JUSTCLOSED',))
        qs = qs.filter(transfer_club_fk__isnull=False)
        if request.user.employee.club_fk is not None:
            qs.filter(cashdesk__club_fk = request.user.employee.club_fk)
        return qs


    def save_model(self, request, obj, form, change):

        # if dont have enough money in cashdesk - print error and abort
        # todo: move to validations
        #if obj.cashdesk.total_amount < obj.amount :
        #    messages.info(request,"Няма достатъчна парична наличност в касата. Налични са :%.2f " % (obj.cashdesk.total_amount,))
        #    return

        obj.save()

        try:
            cashdesk = Cashdesk.objects.get(status = 'OPENED', club_fk = obj.transfer_club_fk)
        except Cashdesk.DoesNotExist:
            messages.error(request,"В момента нямате отворена каса. Моля отворете каса и опитайте пак.")
            obj.amount = 0
            obj.save()
            return

        # add record to Cashdesk_detail_income
        income_doc = Cashdesk_detail_income()
        income_doc.group_fk = Cashdesk_groups_income.objects.get(name='ТРАНСФЕР', sub_name='ТРАНСФЕР')
        income_doc.note = obj.note
        income_doc.amount = obj.amount
        income_doc.transfer_fk = obj
        income_doc.transfer_club_fk = obj.cashdesk.club_fk
        income_doc.cashdesk = cashdesk
        income_doc.save()

        obj.transfer_fk = income_doc
        super(Cashdesk_detail_transferAdmin, self).save_model(request, obj, form, change)


    def get_club_name(self, obj):
        return obj.cashdesk.club_fk.name
    get_club_name.short_description = 'Клуб'

    def has_delete_permission(self, request, obj=None):
        return False

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields

        return ()

admin.site.register(Cashdesk_detail_transfer, Cashdesk_detail_transferAdmin)

class Cashdesk_detail_income_inline(admin.TabularInline):
    model = Cashdesk_detail_income
    fields = ('group_fk', 'note', 'amount', 'order_fk','transfer_club_fk')
    readonly_fields = ('group_fk', 'note', 'amount', 'order_fk','transfer_club_fk')
    extra = 0
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False

class Cashdesk_detail_expense_inline(admin.TabularInline):
    model = Cashdesk_detail_expense
    fields = ('group_fk', 'note', 'amount', 'delivery_fk','transfer_club_fk')
    readonly_fields = ('group_fk', 'note', 'amount', 'delivery_fk','transfer_club_fk')
    extra = 0
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


class CashdeskAdmin(DjangoObjectActions, CompareVersionAdmin):
    list_display = ('rec_date','status','club_fk','beg_open', 'income_amount','expense_amount', 'total_amount','beg_close',)
    readonly_fields = (
        'amt_header','expense_amount','total_amount','beg_amount','end_amount','income_amount','status',
        'id','rec_date','create_date', 'beg_close', 'beg_open', 'club_fk', 'beg_close_date', 'beg_open_date','last_update_date','beg_bank_100', 'beg_bank_50', 'beg_bank_20', 'beg_bank_10', 'beg_bank_5', 'beg_bank_2', 'beg_coin_100', 'beg_coin_50', 'beg_coin_20', 'beg_coin_10', 'beg_coin_5','beg_coin_2','beg_coin_1')

    list_filter = ('rec_date','status', 'club_fk',)
    list_per_page = 50

    date_hierarchy = "rec_date"
    fieldsets = [

        (None, {
            'classes': ('suit-tab', 'suit-tab-daily_turnover',),
            'fields': ['id','status','rec_date','club_fk','beg_close', 'beg_open',]
        }),

        ('Каса в началото на деня', {
            'classes': ('suit-tab', 'suit-tab-Cashdesk_begin',),
            'fields': ['beg_bank_100', 'beg_bank_50', 'beg_bank_20', 'beg_bank_10', 'beg_bank_5', 'beg_bank_2', 'beg_coin_100', 'beg_coin_50', 'beg_coin_20', 'beg_coin_10', 'beg_coin_5', 'beg_coin_2', 'beg_coin_1']
        }),

        ('Каса в края на деня', {
            'classes': ('suit-tab', 'suit-tab-Cashdesk_end',),
            'fields': ['end_bank_100', 'end_bank_50', 'end_bank_20', 'end_bank_10', 'end_bank_5', 'end_bank_2', 'end_coin_100', 'end_coin_50', 'end_coin_20', 'end_coin_10', 'end_coin_5', 'end_coin_2', 'end_coin_1',]
        }),

        ('Други', {
            'classes': ('suit-tab', 'suit-tab-оther',),
            'fields': [ 'beg_close_date','beg_open_date','create_date', 'last_update_date',]
        }),

        (None, {
            'fields': [('amt_header','beg_amount','income_amount','expense_amount','total_amount','end_amount',),]
        }),

    ]

    suit_form_tabs = (('daily_turnover', 'Дневен оборот'),
                          ('Cashdesk_begin', 'Каса в началото на деня'),
                          ('Cashdesk_end', 'Каса в края на деня'),
                          ('оther', 'Други'),)

    inlines = [
        Cashdesk_detail_income_inline,
        # Cashdesk_detail_income_inline_add,
        Cashdesk_detail_expense_inline,
        # Cashdesk_detail_expense_inline_add,
    ]

    def get_queryset(self, request):
        qs = super(CashdeskAdmin, self).get_queryset(request)
        if request.user.employee.club_fk is None:
            return qs

        return qs.filter(club_fk = request.user.employee.club_fk).filter(status__in = ('OPENED','JUSTCLOSED',))

    def get_readonly_fields(self, request, obj=None):

        if obj and obj.status != 'OPENED':
            return self.readonly_fields + ('end_bank_100', 'end_bank_50', 'end_bank_20', 'end_bank_10', 'end_bank_5', 'end_bank_2', 'end_coin_100', 'end_coin_50', 'end_coin_20', 'end_coin_10', 'end_coin_5', 'end_coin_2', 'end_coin_1')

        return self.readonly_fields

    def cashdeskclose(self, request, obj):

        if obj.status != 'OPENED':
            messages.error(request,"Грешка: Може да приключите само отворена каса." )
            return

        if obj.end_amount != obj.total_amount:
            messages.error(request,"Грешка: Не съвпадат крайната и очакваната сума. Проверете отчитаната сума или въведете коригиращ ордер. Моля направете необходимата корекция и опитайте отново." )
            return

        obj.beg_close = request.user
        obj.beg_close_date = datetime.now()
        obj.status = 'JUSTCLOSED'
        obj.save()
        messages.info(request,"Успешно приключихте касата.")

    def cashdeskopen(self, request, obj):
        if obj.status != 'JUSTCLOSED':
            messages.error(request,"Грешка: Може да отворите само последно затворена каса." )
            return

        newCashdesk=Cashdesk()
        newCashdesk.rec_date =obj.rec_date +timedelta(days=1)

        newCashdesk.beg_bank_100 = obj.end_bank_100
        newCashdesk.beg_bank_50  = obj.end_bank_50
        newCashdesk.beg_bank_20  = obj.end_bank_20
        newCashdesk.beg_bank_10  = obj.end_bank_10
        newCashdesk.beg_bank_5   = obj.end_bank_5
        newCashdesk.beg_bank_2   = obj.end_bank_2
        newCashdesk.beg_coin_100 = obj.end_coin_100
        newCashdesk.beg_coin_50  = obj.end_coin_50
        newCashdesk.beg_coin_20  = obj.end_coin_20
        newCashdesk.beg_coin_10  = obj.end_coin_10
        newCashdesk.beg_coin_5   = obj.end_coin_5
        newCashdesk.beg_coin_2   = obj.end_coin_2
        newCashdesk.beg_coin_1   = obj.end_coin_1

        newCashdesk.beg_open = request.user
        newCashdesk.beg_open_date = datetime.now()
        newCashdesk.club_fk = obj.club_fk
        newCashdesk.create_date = datetime.now()
        newCashdesk.last_update_date = datetime.now()
        newCashdesk.save()

        obj.status = 'CLOSED'
        obj.save()
        messages.info(request,"Успешно нова касата.")
        return redirect(newCashdesk.get_admin_url())


    cashdeskclose.label = "Приключване"
    cashdeskclose.short_description = "Приключване на каса"

    cashdeskopen.label = "Отваряне"
    cashdeskopen.short_description = "Отваряне на каса"

    change_actions = ('cashdeskclose','cashdeskopen')

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

admin.site.register(Cashdesk, CashdeskAdmin)