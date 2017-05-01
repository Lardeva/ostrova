from datetime import timedelta

from django.contrib import admin
from django.contrib import messages
from django.contrib.auth.admin import UserAdmin
from django.core.urlresolvers import reverse_lazy
from django.forms import ModelChoiceField
from django.shortcuts import redirect
from django_object_actions import DjangoObjectActions
from django_select2.forms import ModelSelect2Widget
from reversion_compare.admin import CompareVersionAdmin

from ostrovaCalendar.clever_select_enhanced.clever_txt_field import ChainedNumberInputField
from ostrovaCalendar.clever_select_enhanced.form_fields import ChainedModelChoiceField
from ostrovaCalendar.clever_select_enhanced.forms import ChainedChoicesModelForm

from ostrovaCalendar.models import *

class DeliveryDetailForm(ChainedChoicesModelForm):

    article_fk = ChainedModelChoiceField(parent_field='group_fk', ajax_url=reverse_lazy('article_ajax_chained_models'),
                                      label=u'Артикул', required=True,model=Article, additional_related_field='delivery_fk__supplier_fk')

    group_fk = ChainedModelChoiceField(parent_field='supplier_fk', inline_fk_to_master='delivery_fk', ajax_url=reverse_lazy('article_ajax_chained_models'),
                                         label=u'Артикулна група', required=True,model=ArticleGroup )

    price = ChainedNumberInputField(parent_field='article_fk', ajax_url=reverse_lazy('article_ajax_chained_models'),
                                         label=u'Цена', required=True )

    class Meta:
        model = DeliveryDetail
        fields = '__all__'
        # widgets = {
        #     'code': TextInput(attrs={'style':'width:80px'}),
        #     'nadpis': TextInput(attrs={'style':'width:500px'}),
        # }


class DeliveryDetailInline(admin.TabularInline):
    model = DeliveryDetail
    form = DeliveryDetailForm

    fields = ('group_fk','article_fk','price','cnt','price_final',)

    select_related = ('group', 'article')

    readonly_fields = ('price_final',)

    def price_final(self,obj):
        return nvl(obj.price,0)*nvl(obj.cnt,0)


class DeliveryAdmin(CompareVersionAdmin):
    list_display = ('id','club_fk','order_date', 'delivery_date', 'supplier_fk', 'invoice_no','firm_invoice_no','status', 'paid','delivery_amount',)
    # list_editable = ('club_fk','status')

    def get_form(self, request, obj=None, **kwargs):

         form = super(DeliveryAdmin, self).get_form(request, obj,**kwargs)

         # if edditing (obj will be filled in with the exeistin model)
         if obj:
              # alternatives for readonly:
              # form.base_fields['supplier_fk'].widget.attrs.update({'readonly':'True','style':'pointer-events:none'})
              # form.base_fields['club_fk'].widget = django.forms.widgets.Select(attrs={'readonly':'True','onfocus':"this.defaultIndex=this.selectedIndex;", 'onchange':"this.selectedIndex=this.defaultIndex;"})
              form.base_fields['supplier_fk'].disabled = True
              form.base_fields['club_fk'].disabled = True


         # if club is specified for the current user (in the user model), do not allow choosing another club
         if request.user.employee.club_fk:
             form.base_fields['club_fk'].initial = request.user.employee.club_fk
             form.base_fields['club_fk'].widget.attrs.update({'readonly':'True','style':'pointer-events:none'})  # simulates readonly on the browser with the help of css
             #form.base_fields['club_fk'].disabled = True  - does not work well on add new operation's on save

         return form

    readonly_fields = ('id','delivery_amount','user', 'last_update_date', 'order_date', 'delivery_date')

    fieldsets = [
        (None, {
            'classes': ('suit-tab', 'suit-tab-provider',),
            'fields': ['id','supplier_fk','order_date','delivery_date','invoice_no','firm_invoice_no','club_fk','status','paid','delivery_amount',]
        }),

        ('Забележки', {
            'classes': ('suit-tab', 'suit-tab-notes',),
            'fields': ['notes','user','last_update_date',]
        }),
    ]

    suit_form_tabs = (('provider', 'Доставка'), ('notes', 'Забележки'))

    inlines = [
        DeliveryDetailInline,
    ]

    def save_model(self, request, obj, form, change):

        ###############################################################
        # Handle payment
        ###############################################################
        if 'paid' in form.changed_data and form.cleaned_data['paid'] == 'ДА':
            payment_doc = Cashdesk_detail_expense()

            payment_doc.delivery_fk = obj
            payment_doc.amount = obj.delivery_amount
            payment_doc.name = str(obj)
            payment_doc.cashdesk_groups_expense_fk = Cashdesk_groups_expense.objects.get(name='ДОСТАВКА',sub_name='ПЛАЩАНЕ')
            payment_doc.cashdesk = Cashdesk.objects.filter(club_fk=obj.club_fk).latest('id')

            payment_doc.save()

            messages.info(request,"Добавено плащане за %.2f лв. Номер:%d, Каса:%s " % (payment_doc.amount,payment_doc.id, str(payment_doc.cashdesk)))

        ###############################################################
        # Handle store record
        ###############################################################

        if 'status' in form.changed_data and form.cleaned_data['status'] == 'ДОСТАВЕНО':
            # todo: add store record

            obj.delivery_date = datetime.now()

        ###############################################################
        # Handle misc data
        ###############################################################

        obj.last_update_date = datetime.now()
        obj.user = request.user
        if request.user.employee.club_fk:
            obj.club_fk = request.user.employee.club_fk

        super(DeliveryAdmin, self).save_model(request, obj, form, change)

admin.site.register(Delivery, DeliveryAdmin)


class ClubAdmin(admin.ModelAdmin):
    fields = ('name', 'hall_price', 'address',)
    list_display =( 'name', 'hall_price', 'address',)

admin.site.register(Club, ClubAdmin)


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


class ArticleForm(ChainedChoicesModelForm):
    article = ChainedModelChoiceField(parent_field='group', ajax_url=reverse_lazy('article_ajax_chained_models'),
                                      label=u'Артикул', required=True,model=Article )

    class Meta:
        model = Article
        fields = '__all__'


class  ArticleInline(admin.TabularInline):
    model = Article
    form = ArticleForm
    select_related = ('group', 'article')





class ArticleStoreAdmin(CompareVersionAdmin):
    readonly_fields = ('id',)
    list_display = ('id','club_fk','article_fk', 'cnt', 'cnt_min', 'cnt_bl',)
admin.site.register(ArticleStore, ArticleStoreAdmin)

class OrderDetailForm(ChainedChoicesModelForm):

    #article_fk = ChainedModelChoiceField(parent_field='group_fk', ajax_url=reverse_lazy('article_ajax_chained_models'),
#                                      label=u'Артикул', required=True,model=Article )

    # article_fk = ModelChoiceField(
    #     queryset=Article.objects.filter(active=True),
    #     label='Артикул',
    #     widget=ModelSelect2Widget(
    #         model=Article,
    #         search_fields=['name__icontains'],
    #         max_results=100,
    #         dependent_fields={'orderdetail_set-0-group_fk': 'group_fk'},
    #     )
    # )

    class Meta:
        model = OrderDetail
        fields = '__all__'
        # widgets = {
        #     'code': TextInput(attrs={'style':'width:80px'}),
        #     'nadpis': TextInput(attrs={'style':'width:500px'}),
        # }


class OrderDetailInline(admin.TabularInline):
    model = OrderDetail
    form = OrderDetailForm
#    select_related = ('group', 'article')

    raw_id_fields = ( 'article_fk',)


class OrderAdmin(CompareVersionAdmin):

    change_list_template = "admin/ostrovaCalendar/order/change_list.html"
    search_fields = ('child','parent','phone',)
    list_filter     = (
        'rec_date','club_fk',
    )

    ordering        = ['-id']
    list_per_page = 50

    date_hierarchy = "rec_date"

    list_display = ('rec_date', 'club_fk', 'rec_time', 'parent', 'child', 'hall_count', 'locked', 'payed_final',)
    fieldsets = [
        (None, {
            'classes': ('suit-tab', 'suit-tab-club',),
            'fields': ['club_fk','rec_date','rec_time_slot','locked','user']
        }),

        ('Клиент', {
            'classes': ('suit-tab', 'suit-tab-club',),
            'fields': ['parent','phone','child','age','child_count','adult_count','saloon_fk','address','email',]
        }),

        ('Плащане1', {
            'classes': ('suit-tab', 'suit-tab-club',),
            'fields': ['deposit','discount','price_final','payment_date',]
        }),

        ('Плащане2', {
            'classes': ('suit-tab', 'suit-tab-club',),
            'fields': ['deposit2_date','deposit2','payed_final',]
        }),

        ('Забележка', {
            'classes': ('suit-tab', 'suit-tab-notes',),
            'fields': ['order_date', 'create_date','last_update_date','changes','update_state','notes','refusal_date','refusal_reason','notes_torta','notes_kitchen',]
        }),
    ]

    suit_form_tabs = (('club', 'Поръчка за парти'),
                      # ('order', 'Поръчка за парти'),
                      # ('client', 'Client'),
                      #('paymends1', 'Paymends1'),
                      #('paymends2', 'Paymends2'),
                      ('notes', 'Забележки'))

    def locked(self, obj):
        return len(obj.locked_set.all())

    def suit_row_attributes(self, obj):
        class_locked = {
            '0': 'success',
            '1': 'warning',
        }
        css_class = class_locked.get(obj.locked)
        if css_class:
            return {'class': css_class}

    def suit_cell_attributes(self, obj, column):
        if column == 'locked':
            return {'class': 'text-center'}
        elif column == 'right_aligned':
            return {'class': 'text-right muted'}

    inlines = [
        OrderDetailInline,
    ]

    def save_model(self, request, obj, form, change):

        if 'deposit' in form.changed_data and form.cleaned_data['deposit'] > 0:
            payment_doc = Cashdesk_detail_income()

            payment_doc.order_fk = obj
            payment_doc.amount = obj.deposit
            payment_doc.name = str(obj)
            payment_doc.cashdesk_groups_income_fk = Cashdesk_groups_income.objects.get(name='ПОРЪЧКА',sub_name='ПЛАЩАНЕ')
            payment_doc.cashdesk = Cashdesk.objects.filter(club_fk=obj.club_fk).latest('id')

            payment_doc.save()

            messages.info(request,"Добавено плащане капаро за %.2f лв. Номер:%d, Каса:%s " % (payment_doc.amount,payment_doc.id, str(payment_doc.cashdesk)))

        if 'deposit2' in form.changed_data and form.cleaned_data['deposit2'] > 0:
            payment_doc = Cashdesk_detail_income()

            payment_doc.order_fk = obj
            payment_doc.amount = obj.deposit2
            payment_doc.name = str(obj)
            payment_doc.cashdesk_groups_income_fk = Cashdesk_groups_income.objects.get(name='ПОРЪЧКА',sub_name='ПЛАЩАНЕ')
            payment_doc.cashdesk = Cashdesk.objects.filter(club_fk=obj.club_fk).latest('id')

            payment_doc.save()

            messages.info(request,"Добавено плащане капаро 2 за %.2f лв. Номер:%d, Каса:%s " % (payment_doc.amount,payment_doc.id, str(payment_doc.cashdesk)))

        if 'payed_final' in form.changed_data and form.cleaned_data['payed_final'] > 0:
            payment_doc = Cashdesk_detail_income()

            payment_doc.order_fk = obj
            payment_doc.amount = obj.payed_final
            payment_doc.name = str(obj)
            payment_doc.cashdesk_groups_income_fk = Cashdesk_groups_income.objects.get(name='ПОРЪЧКА',sub_name='ПЛАЩАНЕ')
            payment_doc.cashdesk = Cashdesk.objects.filter(club_fk=obj.club_fk).latest('id')

            payment_doc.save()

            messages.info(request,"Добавено финално плащане за %.2f лв. Номер:%d, Каса:%s " % (payment_doc.amount,payment_doc.id, str(payment_doc.cashdesk)))

        super(OrderAdmin, self).save_model(request, obj, form, change)

admin.site.register(Order, OrderAdmin)


class SaloonAdmin(admin.ModelAdmin):
    fields = ('club_fk', 'name')

admin.site.register(Saloon, SaloonAdmin)


class TimesAdmin(admin.ModelAdmin):
    fields = ('time_slot',)

admin.site.register(Times, TimesAdmin)


class SupplierAdmin(admin.ModelAdmin):
    fields = ('name',)
admin.site.register(Supplier, SupplierAdmin)


class Cashdesk_detail_incomeAdmin(admin.ModelAdmin):
    fields = ('cashdesk','cashdesk_groups_income_fk','name','amount',)
    list_display =('cashdesk','cashdesk_groups_income_fk','name','amount',)
    readonly_fields = ('cashdesk','cashdesk_groups_income_fk','name','amount',)
    list_filter = ('cashdesk','cashdesk_groups_income_fk','name',)
    search_fields = ('cashdesk','cashdesk_groups_income_fk',)

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields

        return ()

admin.site.register(Cashdesk_detail_income, Cashdesk_detail_incomeAdmin)

class Cashdesk_detail_expenseAdmin(admin.ModelAdmin):
    fields = ('cashdesk','cashdesk_groups_expense_fk','name','amount',)
    list_display =('cashdesk','cashdesk_groups_expense_fk','name','amount',)
    readonly_fields = ('cashdesk','cashdesk_groups_expense_fk','name','amount',)
    list_filter = ('cashdesk','cashdesk_groups_expense_fk','name',)
    search_fields = ('cashdesk','cashdesk_groups_expense_fk',)

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields

        return ()

admin.site.register(Cashdesk_detail_expense, Cashdesk_detail_expenseAdmin)


class Cashdesk_detail_income_inline(admin.TabularInline):
    model = Cashdesk_detail_income
    readonly_fields = ('cashdesk_groups_income_fk', 'name', 'amount', 'delivery_fk')

    extra = 0
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


class Cashdesk_detail_income_inline_add(admin.TabularInline):
    model = Cashdesk_detail_income

    readonly_fields = ('delivery_fk',)

    extra = 1
    can_delete = False
    verbose_name = ''
    verbose_name_plural = ''

    def has_change_permission(self, request, obj=None):
        return False


class Cashdesk_detail_expense_inline(admin.TabularInline):
    model = Cashdesk_detail_expense
    readonly_fields = ('cashdesk_groups_expense_fk', 'name', 'amount', 'order_fk')

    raw_id_fields = ("order_fk",)

    extra = 1

    can_delete = False

    def has_add_permission(self, request, obj=None):
            return False


class Cashdesk_detail_expense_inline_add(admin.TabularInline):
    model = Cashdesk_detail_expense

    readonly_fields = ('order_fk',)

    extra = 1
    can_delete = False
    verbose_name = ''
    verbose_name_plural = ''

    def has_change_permission(self, request, obj=None):
        return False


class Cashdesk_groups_incomeAdmin(admin.ModelAdmin):
    fields = ('name', 'sub_name',)
    list_display = ('name', 'sub_name',)

admin.site.register(Cashdesk_groups_income, Cashdesk_groups_incomeAdmin)


class Cashdesk_Groups__expenseAdmin(admin.ModelAdmin):
    fields = ('name', 'sub_name',)
    list_display = ('name', 'sub_name',)

admin.site.register(Cashdesk_groups_expense, Cashdesk_Groups__expenseAdmin)


class CashdeskAdmin(DjangoObjectActions, admin.ModelAdmin):
    # fields = ( 'id','rec_date','beg_bank_100', 'beg_bank_50', 'beg_bank_20', 'beg_bank_10', 'beg_bank_5', 'beg_bank_2', 'beg_coin_100', 'beg_coin_50', 'beg_coin_20', 'beg_coin_10', 'beg_coin_5','beg_close', 'beg_open', 'beg_close_date','beg_open_date',
    #            'end_bank_100', 'end_bank_50', 'end_bank_20', 'end_bank_10', 'end_bank_5', 'end_bank_2', 'end_coin_100', 'end_coin_50', 'end_coin_20', 'end_coin_10', 'end_coin_5', 'club_fk', 'create_date', 'last_update_date',)
    list_display = ('id', 'rec_date','end_amount')
    readonly_fields = (
        'amt_header','expense_amount','total_amount','beg_amount','end_amount','income_amount',
        'id','rec_date','create_date', 'beg_close', 'beg_open', 'club_fk', 'beg_close_date', 'beg_open_date','last_update_date','beg_bank_100', 'beg_bank_50', 'beg_bank_20', 'beg_bank_10', 'beg_bank_5', 'beg_bank_2', 'beg_coin_100', 'beg_coin_50', 'beg_coin_20', 'beg_coin_10', 'beg_coin_5',)

    fieldsets = [

        (None, {
            'classes': ('suit-tab', 'suit-tab-daily_turnover',),
            'fields': ['id','rec_date','club_fk','beg_close', 'beg_open',]
        }),

        ('Каса в началото на деня', {
            'classes': ('suit-tab', 'suit-tab-Cashdesk_begin',),
            'fields': ['beg_bank_100', 'beg_bank_50', 'beg_bank_20', 'beg_bank_10', 'beg_bank_5', 'beg_bank_2', 'beg_coin_100', 'beg_coin_50', 'beg_coin_20', 'beg_coin_10', 'beg_coin_5',]
        }),

        ('Каса в края на деня', {
            'classes': ('suit-tab', 'suit-tab-Cashdesk_end',),
            'fields': ['end_bank_100', 'end_bank_50', 'end_bank_20', 'end_bank_10', 'end_bank_5', 'end_bank_2', 'end_coin_100', 'end_coin_50', 'end_coin_20', 'end_coin_10', 'end_coin_5',]
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

    def cashdeskclose(self, request, obj):

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

        newCashdesk.beg_close = request.user
        newCashdesk.beg_close_date = datetime.now()
        newCashdesk.club_fk = obj.club_fk
        newCashdesk.create_date = datetime.now()
        newCashdesk.last_update_date = datetime.now()
        newCashdesk.save()

        return redirect(newCashdesk.get_admin_url())


    cashdeskclose.label = "Приключване"  # optional
    cashdeskclose.short_description = "Приключване на каса"  # optional

    change_actions = ('cashdeskclose', )

    def has_add_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return False

admin.site.register(Cashdesk, CashdeskAdmin)


class ScheduleAdmin(admin.ModelAdmin):
    list_display =('schedule_date','times_fk','order_fk',)
    fields =('schedule_date','times_fk','order_fk',)
    list_display_links = ('schedule_date','times_fk','order_fk',)
    raw_id_fields = ("order_fk",)
    # list_editable = ("order_fk",)

    ordering = ( 'schedule_date', 'times_fk__time_slot' )
    list_filter = (
        'schedule_date', 'club_fk','times_fk',
    )

    list_per_page = 35

    def suit_row_attributes(self, obj, request=None):
        return {'class': 'ostrova_cal_row'}

    # def suit_cell_attributes(self, obj, column):
        #     if column == 'order_fk':
        #
        #         if not obj.order_fk:
        #             css_class = 'ostrova_free'
        #         else:
        #             if obj.order_fk.deposit_date:
        #                 css_class = 'ostrova_deposit'
        #             else:
        #                 css_class = 'ostrova_no_deposit'
        #
        #         if css_class:
        #             return {'class': css_class}


    def suit_cell_attributes(self, obj, column):
        if column == 'order_fk':

            if obj.order_fk:
                if obj.order_fk.deposit_date:
                     css_class = 'ostrova_deposit'
                else:
                     css_class = 'ostrova_no_deposit'

                if css_class:
                     return {'class': css_class}

admin.site.register(Schedule, ScheduleAdmin)


# Define an inline admin descriptor for Employee model
# which acts a bit like a singleton
class EmployeeInline(admin.StackedInline):
    model = Employee
    can_delete = False
    verbose_name_plural = 'Допълнителни данни за служител'

# Define a new User admin
class EmployeeAdmin(UserAdmin):
    inlines = (EmployeeInline, )

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, EmployeeAdmin)



# class StockAcceptance_detailAdmin(admin.ModelAdmin):
#
#     fields = ('article_fk', 'deliverydetail_fk', 'cnt','name',)
#     list_display =('article_fk', 'deliverydetail_fk', 'cnt','name',)
#
# admin.site.register(stock_acceptance_detail, StockAcceptance_detailAdmin)
#
#
# class StockDelivery_detailAdmin(admin.ModelAdmin):
#
#     fields = ('article_fk', 'orderdetail_fk', 'cnt',)
#     list_display =('article_fk', 'orderdetail_fk', 'cnt',)
#admin.site.register(stock_delivery_detail, StockDelivery_detailAdmin)


class stock_delivery_detail_inline(admin.TabularInline):
    model = stock_delivery_detail

    #readonly_fields = ('delivery_fk',)

    raw_id_fields = ("orderdetail_fk",)
    extra = 5


class stock_acceptance_detail_inline(admin.TabularInline):
    model = stock_acceptance_detail
    #readonly_fields = ('cashdesk_groups_expense_fk', 'name', 'amount', 'order_fk')

    raw_id_fields = ("deliverydetail_fk",)

    extra = 5


class stock_receipt_protocolAdmin(admin.ModelAdmin):

    fields = ('id', 'type','club_fk', 'receipt_date','note',)
    list_display =('id','receipt_date','type', 'club_fk', )
    readonly_fields = ('id', )

    inlines = [
        stock_delivery_detail_inline,
        stock_acceptance_detail_inline,
    ]

def stock_receipt_protocolclose(self, request, obj):

    newstock_receipt_protocol=stock_receipt_protocol()
    newstock_receipt_protocol.rec_date =obj.rec_date +timedelta(days=1)


stock_receipt_protocolclose.label = "Приключване"  # optional
stock_receipt_protocolclose.short_description = "Приключване на протокол"  # optional

change_actions = ('stock_receipt_protocolclose', )


def has_add_permission(self, request, obj=None):
    return True

def has_delete_permission(self, request, obj=None):
    return False

admin.site.register(stock_receipt_protocol, stock_receipt_protocolAdmin)