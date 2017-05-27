from datetime import timedelta, datetime

from decimal import Decimal

from adminextensions.list_display import related_field
from django.contrib.admin import ModelAdmin
from django.contrib.admin.sites import site
from django.contrib.admin import widgets
from django.contrib import admin
from django.contrib import messages
from django.contrib.admin.utils import flatten
from django.contrib.admin.widgets import ForeignKeyRawIdWidget, AdminDateWidget, AdminTimeWidget
from django.contrib.auth.admin import UserAdmin
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse_lazy
from django.forms import ModelChoiceField, ModelForm, TextInput, BaseInlineFormSet, TimeInput, DateTimeInput
from django.shortcuts import redirect
from django_object_actions import DjangoObjectActions
from django_select2.forms import ModelSelect2Widget
from reversion_compare.admin import CompareVersionAdmin
from suit.widgets import SuitTimeWidget

from ostrovaCalendar.clever_select_enhanced.clever_txt_field import ChainedNumberInputField
from ostrovaCalendar.clever_select_enhanced.form_fields import ChainedModelChoiceField
from ostrovaCalendar.clever_select_enhanced.forms import ChainedChoicesModelForm

from ostrovaCalendar.models import *
from ostrovaweb.utils import RequiredFormSet


class DeliveryDetailForm(ChainedChoicesModelForm):

    price = ChainedNumberInputField(parent_field='article_fk', ajax_url=reverse_lazy('article_ajax_chained_models'),
                                         label='Единична цена', required=True )

    def clean_amount(self):
        self.cleaned_data['amount'] = round(Decimal(self.cleaned_data.get('price',0)) * Decimal(self.cleaned_data.get('cnt',0)),2)
        return self.cleaned_data['amount']

    class Meta:
        model = DeliveryDetail
        fields = '__all__'


class DeliveryDetailInline(admin.TabularInline):
    model = DeliveryDetail
    form = DeliveryDetailForm

    fields = ('article_fk','cnt','price','amount',)

    select_related = ('group', 'article')

    raw_id_fields = ( 'article_fk', )

    readonly_fields = ()

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.is_closed():
            self.form = ModelForm
            return self.fields
        return self.readonly_fields

    def get_extra(self, request, obj=None, **kwargs):
        if obj and obj.is_closed():
            return 0
        return self.extra

    def get_max_num(self, request, obj=None, **kwargs):
        if obj and obj.is_closed():
            return 0
        return self.max_num

    def has_delete_permission(self, request, obj=None):
        if obj and obj.is_closed():
            return False
        return True


class DeliveryAdmin(DjangoObjectActions, CompareVersionAdmin):
    list_display = ('id','club_fk','order_date', 'delivery_date', 'supplier_fk', 'invoice_no','firm_invoice_no','status', 'paid','delivery_amount',)
    # list_editable = ('club_fk','status')
    search_fields = ('club_fk__name','order_date','supplier_fk__name',)
    list_filter     = (
        'order_date','club_fk','supplier_fk',
    )

    ordering = ['-id']
    list_per_page = 50
    date_hierarchy = "order_date"

    def get_inline_formsets(self, request, formsets, inline_instances,obj=None):
        formsets = super(DeliveryAdmin, self).get_inline_formsets(request, formsets, inline_instances, obj)

        for fm in formsets:
            form = fm.formset.form
            if 'amount' in form.base_fields:
               form.base_fields['amount'].disabled = True
               form.base_fields['amount'].widget.attrs.update({'readonly':'True','style':'pointer-events:none'})

        return formsets

    def get_form(self, request, obj=None, **kwargs):

        form = super(DeliveryAdmin, self).get_form(request, obj,**kwargs)

        if obj:
            form.base_fields['supplier_fk'].disabled = True
            form.base_fields['club_fk'].disabled = True

        # if club is specified for the current user (in the user model), do not allow choosing another club
        if request.user.employee.club_fk:
            form.base_fields['club_fk'].initial = request.user.employee.club_fk
            form.base_fields['club_fk'].widget.attrs.update({'readonly':'True','style':'pointer-events:none'})  # simulates readonly on the browser with the help of css

        return form

    readonly_fields = ('id','delivery_amount','user', 'last_update_date', 'order_date', 'delivery_date','cashdesk_fk','status','paid')
    closed_readonly_fields = readonly_fields + ( 'invoice_no', 'firm_invoice_no', 'notes')

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.is_closed():
            return self.closed_readonly_fields
        return self.readonly_fields

    fieldsets = [
        (None, {
            'classes': ('suit-tab', 'suit-tab-provider',),
            'fields': ['id','supplier_fk','order_date','delivery_date','cashdesk_fk','invoice_no','firm_invoice_no','club_fk','status','paid','delivery_amount',]
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

        if obj.id is None:
            obj.delivery_date = datetime.now()

        obj.last_update_date = datetime.now()
        obj.user = request.user
        if request.user.employee.club_fk:
            obj.club_fk = request.user.employee.club_fk

        obj.save()

        super(DeliveryAdmin, self).save_model(request, obj, form, change)

    def deliver(self, request, obj):

        if obj.status != 'ORDERED':
            messages.error(request,"Грешка: Може да доставите само отворена доставка." )
            return

        # add stock_receipt_protocol
        delivery_doc = stock_receipt_protocol()
        delivery_doc.delivery_fk = obj
        delivery_doc.club_fk = obj.club_fk
        delivery_doc.delivery_date = datetime.now()
        delivery_doc.type = 'DELIVERY'
        delivery_doc.note = 'Протокол към доставка Номер %d Дата:%s' % (obj.id,obj.delivery_date)
        delivery_doc.closed = True
        delivery_doc.save()

        for delivery_dev in obj.deliverydetail_set.all():

            # lookup store from the other side
            try:
                artstore = ArticleStore.objects.get(club_fk = obj.club_fk, article_fk = delivery_dev.article_fk)
            except ArticleStore.DoesNotExist:
                artstore = ArticleStore()
                artstore.club_fk = obj.club_fk
                artstore.article_fk = delivery_dev.article_fk
                artstore.cnt = 0
                artstore.cnt_min = 0
                artstore.cnt_bl = 0

            artstore.cnt +=  delivery_dev.cnt
            artstore.save()

            # add stock_acceptance_detail for each deliveydetail
            delivery_acc = stock_acceptance_detail()
            delivery_acc.stock_protocol_fk = delivery_doc
            delivery_acc.article_store_fk = artstore
            delivery_acc.cnt = delivery_dev.cnt
            delivery_acc.save()

            messages.info(request,"Добавен е запис за доставка в склада за %s. налични:%d, " % (str( delivery_dev.article_fk),artstore.cnt, ) )

        obj.status = 'DELIVERED'
        obj.save()

    def cancel(self, request, obj):

        if obj.status != 'ORDERED':
            messages.error(request,"Грешка: Може да откажете само отворена доставка.")
            return

        obj.status = 'CANCELED'
        obj.save()

    def pay(self, request, obj):

        if obj.paid != 'No':
            messages.error(request,"Грешка: Може да платите само неплатена доставка.")
            return

        try:
            cashdesk = Cashdesk.objects.get(club_fk=obj.club_fk,status='OPENED')
        except Cashdesk.DoesNotExist:
            messages.error(request,"В момента нямате отворена каса. Моля отворете каса и опитайте пак.")
        else:
            payment_doc = Cashdesk_detail_expense()
            payment_doc.delivery_fk = obj
            payment_doc.amount = obj.delivery_amount
            payment_doc.note = str(obj.notes)
            payment_doc.group_fk = Cashdesk_groups_expense.objects.get(name='ДОСТАВКА',sub_name='ПЛАЩАНЕ')
            payment_doc.cashdesk = cashdesk
            payment_doc.save()
            messages.info(request,"Добавено плащане за %.2f лв. Номер:%d, Каса:%s " % (payment_doc.amount,payment_doc.id, str(payment_doc.cashdesk)))

            obj.cashdesk_fk = cashdesk
            obj.paid = 'Yes'
            obj.save()

    deliver.label = "Доставяне"
    deliver.short_description = "Доставяне"

    cancel.label = "Отказ"
    cancel.short_description = "Отказ"

    pay.label = "Плащане"
    pay.short_description = "Плащане"

    change_actions = ('deliver', 'cancel','pay')

admin.site.register(Delivery, DeliveryAdmin)

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
            newCashdesk.beg_coin_2   = 0
            newCashdesk.beg_coin_1   = 0

            newCashdesk.beg_open = request.user
            newCashdesk.beg_open_date = datetime.now()
            newCashdesk.club_fk = obj
            newCashdesk.create_date = datetime.now()
            newCashdesk.last_update_date = datetime.now()
            newCashdesk.status = 'OPENED'
            newCashdesk.save()
        super(ClubAdmin,self).save_model(request, obj, form, change)

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
    search_fields = ('name', 'description','id')

admin.site.register(Article, ArticleAdmin)


# class ArticleOrderFilter(admin.SimpleListFilter):
#
#     title = 'Група'
#     parameter_name  = 'grp_fk'
#
#     def __init__(self, field, request, params, model, model_admin, field_path):
#         super(ArticleOrderFilter,self).__init__(request, params, model, model_admin)
#
#     def lookups(self, request, model_admin,):
#         lst = []
#         queryset = ArticleGroup.objects.filter(order_type = True)
#         for group in queryset:
#             lst.append(
#                 (str(group.id), str(group))
#             )
#         return lst # sorted(lst, key=lambda tp: tp[1])
#
#     def queryset(self, request, queryset):
#         if self.value():
#             return queryset.filter(group_fk=self.value())
#
#     # def queryset(self, request, queryset):
#     #          return queryset.filter(group_fk__order_type = True)
#
class ArticleOrderForm(ModelForm):

    def __init__(self,*args,**kwargs):
        super(ArticleOrderForm, self).__init__(*args,**kwargs)
        self.fields['group_fk'].queryset=ArticleGroup.objects.filter(order_type = True)

class ArticleOrderAdmin(admin.ModelAdmin):
    fields = ('id','name', 'description','measure','last_update_date','group_fk','sale_price',)
    list_display =('name','group_fk','description','measure','delivery_price','sale_price',)
    readonly_fields = ('last_update_date','id',)
    form = ArticleOrderForm

    list_filter = (
        ('group_fk', admin.RelatedOnlyFieldListFilter),
    )
    search_fields = ('id', 'name', 'description')

admin.site.register(ArticleOrder, ArticleOrderAdmin)


class ArticleDeliveryForm(ModelForm):

    def __init__(self,*args,**kwargs):
        super(ArticleDeliveryForm, self).__init__(*args,**kwargs)
        self.fields['group_fk'].queryset=ArticleGroup.objects.filter(delivery_type = True)


class ArticleDeliveryAdmin(admin.ModelAdmin):
    fields = ('id','name', 'description','measure','last_update_date','group_fk','delivery_price',)
    list_display =('name','group_fk','description','measure','delivery_price','sale_price',)
    readonly_fields = ('last_update_date','id',)
    form = ArticleDeliveryForm

    list_filter = (
        ('group_fk', admin.RelatedOnlyFieldListFilter),
    )
    search_fields = ('id', 'name', 'description')

admin.site.register(ArticleDelivery, ArticleDeliveryAdmin)
# class ArticleForm(ChainedChoicesModelForm):
#     article = ChainedModelChoiceField(parent_field='group', ajax_url=reverse_lazy('article_ajax_chained_models'),
#                                       label=u'Артикул', required=True,model=Article )
#
#     class Meta:
#         model = Article
#         fields = '__all__'


# class  ArticleInline(admin.TabularInline):
#     model = Article
#     form = ArticleForm
#     select_related = ('group', 'article')

class ArticleStoreForm(ModelForm):

    def clean(self):
        if self.cleaned_data['cnt_bl'] > self.instance.cnt:
            raise ValidationError("Не може да се блокира количество по-голямо от наличното в склада." )
        return self.cleaned_data

    class Meta:
        model = DeliveryDetail
        fields = '__all__'


class ArticleStoreAdmin(CompareVersionAdmin):
    form = ArticleStoreForm
    readonly_fields = ('id','club_fk','article_fk','cnt','user','create_date','last_update_date')
    fields = ('club_fk','article_fk','user','create_date','last_update_date','cnt','cnt_min', 'cnt_bl','note')
    list_display = ('id','club_fk','article_fk', 'cnt', 'cnt_min', 'cnt_bl','note')
    search_fields = ('article_fk','article_fk__name','article_fk__group_fk__name',)
    raw_id_fields = ('article_fk',)
    list_filter     = (
       'club_fk',
       # 'article_fk__group_fk__name',
    )
    list_per_page = 50

    def save_model(self, request, obj, form, change):

        obj.last_update_date = datetime.now()
        obj.user = request.user
        super(ArticleStoreAdmin, self).save_model(request, obj, form, change)


    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(ArticleStore, ArticleStoreAdmin)

class OrderDetailForm(ChainedChoicesModelForm):

    price = ChainedNumberInputField(parent_field='article_fk', ajax_url=reverse_lazy('article_ajax_chained_order_models'),
                                    label=u'Цена', required=True )

    def clean_amount(self):
        self.cleaned_data['amount'] = round(Decimal(nvl(self.cleaned_data.get('price',0),0)) * Decimal(nvl(self.cleaned_data.get('cnt',0),0)),2)
        return self.cleaned_data['amount']

    class Meta:
        model = OrderDetail
        fields = '__all__'


class OrderDetailInline(admin.TabularInline):
    model = OrderDetail
    form = OrderDetailForm
    readonly_fields = ()
    fields = ('article_fk', 'cnt', 'price', 'amount')

    raw_id_fields = ( 'article_fk',)

    def get_readonly_fields(self, request, obj=None):
        if obj:
           if (obj.locked and not request.user.is_superuser or
               obj.store_status
           ):
            self.form = ModelForm
            return self.fields
        return self.readonly_fields

    def get_extra(self, request, obj=None, **kwargs):
        if obj:
            if (obj.locked and not request.user.is_superuser or
                    obj.store_status
            ):
                return 0
        return self.extra

    def get_max_num(self, request, obj=None, **kwargs):
        if obj:
            if (obj.locked and not request.user.is_superuser or
                    obj.store_status
            ):
                return 0
        return self.max_num

    def has_delete_permission(self, request, obj=None):
        if obj:
            if (obj.locked and not request.user.is_superuser or
                    obj.store_status
            ):
                return False
        return True

class OrderForm(ChainedChoicesModelForm):


    saloon_fk = ChainedModelChoiceField(parent_field='club_fk', ajax_url=reverse_lazy('saloon_ajax_chained_models'),
                                    label=u'Салон', required=True, model=Saloon )

    def clean(self):

        if ':' not in self.cleaned_data['rec_time']:
            self.cleaned_data['rec_time'] += ':00'
        if ':' not in self.cleaned_data['rec_time_end']:
            self.cleaned_data['rec_time_end'] += ':00'

        if self.cleaned_data['rec_time'].count(':') == 2:
            self.cleaned_data['rec_time'] = self.cleaned_data['rec_time'].rsplit(':',1)[0]
        if self.cleaned_data['rec_time_end'].count(':') == 2:
            self.cleaned_data['rec_time_end'] = self.cleaned_data['rec_time_end'].rsplit(':',1)[0]

        try:
            datetime.strptime(self.cleaned_data['rec_time'], '%H:%M')
        except ValueError:
            raise ValueError("Невалиден формат за начален час. Трябва да бъде час, час:минути или час:минути:секунди")

        try:
            datetime.strptime(self.cleaned_data['rec_time_end'], '%H:%M')
        except ValueError:
            raise ValueError("Невалиден формат за краен час. Трябва да бъде час, час:минути или час:минути:секунди")

        # rec_time triabva da e po-malko ot rec_time_end
        if datetime.strptime(self.cleaned_data['rec_time'], '%H:%M') > datetime.strptime(self.cleaned_data['rec_time_end'], '%H:%M'):
                raise ValidationError("Моля изберете по-малък начален час от крайният")

        if datetime.strptime(self.cleaned_data['rec_time'], '%H:%M').hour < 10:
            raise ValidationError("Моля изберете по-голям начален час от 10 часа")

        if datetime.strptime(self.cleaned_data['rec_time_end'], '%H:%M').hour > 21:
            raise ValidationError("Моля изберете по-малък начален час от 21 часа")

        # da se proveri (sas filter ot bazata) dali ima veche rojden den za tazi data i chas i klub
        orders = Order.objects.filter(rec_date= self.cleaned_data['rec_date'], club_fk=self.cleaned_data['club_fk']).exclude(id=self.instance.id)
        for order in orders:
            if datetime.strptime(self.cleaned_data ['rec_time'],'%H:%M' )<= datetime.strptime(order.rec_time_end,'%H:%M') and datetime.strptime(self.cleaned_data['rec_time'],'%H:%M')>= datetime.strptime(order.rec_time,'%H:%M'):
                raise ValidationError('Моля изберете други часове за начало и край на поръчката. Времената се припокриват - друга заявка в  ' +order.rec_time + ' и ' + order.rec_time_end +'.' )
            if datetime.strptime(self.cleaned_data ['rec_time_end'],'%H:%M')>= datetime.strptime(order.rec_time,'%H:%M') and datetime.strptime(self.cleaned_data['rec_time_end'],'%H:%M')<= datetime.strptime(order.rec_time_end,'%H:%M'):
                raise ValidationError('Моля изберете други часове за начало и край на поръчката. Времената се припокриват - друга заявка започва в '+order.rec_time +'.' )
            if datetime.strptime(self.cleaned_data ['rec_time'],'%H:%M')<= datetime.strptime(order.rec_time,'%H:%M') and datetime.strptime(self.cleaned_data['rec_time_end'],'%H:%M')>= datetime.strptime(order.rec_time_end,'%H:%M'):
                raise ValidationError('Моля изберете други часове за начало и край на поръчката. Времената се припокриват - друга заявка в '+order.rec_time+ '.')

        # todo: rec_date triabva da e > datetime.now() bez chas

        return self.cleaned_data

    class Meta:
        model = Order
        fields = '__all__'

        widgets = {
            'rec_time': AdminTimeWidget({'format': '%H:%M'}),
            'rec_time_end': AdminTimeWidget,
        }

class OrderAdmin(DjangoObjectActions, ModelAdmin):

    change_list_template = "admin/ostrovaCalendar/order/change_list.html"
    search_fields = ('locked','status','child','parent','phone',)
    list_filter     = (
        'rec_date','club_fk','locked','status',
    )
    form = OrderForm

    ordering        = ['-id']
    list_per_page = 50

    date_hierarchy = "rec_date"
    list_display = ('rec_date', 'club_fk', 'rec_time', 'rec_time_end','parent', 'child', 'status', 'locked', 'priceFinal',)
    fieldsets = [
        (None, {
            'classes': ('suit-tab', 'suit-tab-club',),
            'fields': ('club_fk','rec_date','rec_time','rec_time_end','locked','store_status','status',)
        }),

        ('Клиент', {
            'classes': ('suit-tab', 'suit-tab-club',),
            'fields': ('parent','phone','child','age','child_count','adult_count','saloon_fk','address','email',)
        }),

        ('Суми за плащане', {
            'classes': ('suit-tab', 'suit-tab-club',),
            'fields': ('priceDetail','discount','priceFinal','dueAmount',)
        }),

        ('Плащания', {
            'classes': ('suit-tab', 'suit-tab-club',),
            'fields': ('deposit','deposit2_date','deposit2','payment_date','payed_final',)
        }),

        ('Забележка', {
            'classes': ('suit-tab', 'suit-tab-notes',),
            'fields': ('user','create_date','last_update_date','notes','refusal_date','refusal_reason','notes_torta','notes_kitchen',)
        }),
    ]

    suit_form_tabs = (('club', 'Поръчка за парти'),
                      ('notes', 'Забележки'))


    readonly_fields = ('store_status','locked','create_date','last_update_date','user','priceDetail','dueAmount', 'priceFinal','payment_date','payment_date',)

    # closed_readonly_fields =  tuple(fieldsets[0][1].get('fields')) + tuple(fieldsets[1][1].get('fields')) + tuple(fieldsets[2][1].get('fields')) + tuple(fieldsets[3][1].get('fields')) + tuple(fieldsets[4][1].get('fields'))
    closed_readonly_fields = flatten(x[1].get('fields') for x in fieldsets) # all fields

    def get_readonly_fields(self, request, obj=None):
        if obj:
            if (obj.locked and not request.user.is_superuser or
                    obj.store_status
            ):
                return self.closed_readonly_fields

        return self.readonly_fields

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

    def get_inline_formsets(self, request, formsets, inline_instances,obj=None):
        formsets = super(OrderAdmin, self).get_inline_formsets(request, formsets, inline_instances, obj)

        for fm in formsets:
            form = fm.formset.form
            if 'amount' in form.base_fields:
                form.base_fields['amount'].disabled = True
                form.base_fields['amount'].widget.attrs.update({'readonly':'True','style':'pointer-events:none'})

        return formsets

    def get_form(self, request, obj=None, **kwargs):

        if obj:
            if obj.rec_date < datetime.now().date():
                obj.locked = True
                obj.save()

        form = super(OrderAdmin, self).get_form(request, obj,**kwargs)

        return form

    def save_model(self, request, obj, form, change):

        obj.last_update_date = datetime.now()
        obj.user = request.user

        if request.user.employee.club_fk:
            obj.club_fk = request.user.employee.club_fk

        obj.save()

        if 'deposit' in form.changed_data and form.cleaned_data['deposit'] > 0:
            payment_doc = Cashdesk_detail_income()

            try:
                cashdesk = Cashdesk.objects.get(club_fk=obj.club_fk,status='OPENED')
            except Cashdesk.DoesNotExist:
                messages.error(request,"В момента нямате отворена каса. Моля отворете каса и опитайте пак.")
                obj.deposit = 0
                obj.save()

            payment_doc.order_fk = obj
            payment_doc.amount = obj.deposit
            payment_doc.note = None
            payment_doc.group_fk = Cashdesk_groups_income.objects.get(name='ПОРЪЧКА',sub_name='ПЛАЩАНЕ')
            payment_doc.cashdesk = cashdesk

            payment_doc.save()

            messages.info(request,"Добавено плащане капаро за %.2f лв. Номер:%d, Каса:%s " % (payment_doc.amount,payment_doc.id, str(payment_doc.cashdesk)))

        if 'deposit2' in form.changed_data and form.cleaned_data['deposit2'] > 0:
            payment_doc = Cashdesk_detail_income()

            try:
                cashdesk = Cashdesk.objects.get(club_fk=obj.club_fk,status='OPENED')
            except Cashdesk.DoesNotExist:
                messages.error(request,"В момента нямате отворена каса. Моля отворете каса и опитайте пак.")
                obj.deposit = 0
                obj.save()

            payment_doc.order_fk = obj
            payment_doc.amount = obj.deposit2
            payment_doc.note = None
            payment_doc.group_fk = Cashdesk_groups_income.objects.get(name='ПОРЪЧКА',sub_name='ПЛАЩАНЕ')
            payment_doc.cashdesk = cashdesk

            payment_doc.save()

            messages.info(request,"Добавено плащане капаро 2 за %.2f лв. Номер:%d, Каса:%s " % (payment_doc.amount,payment_doc.id, str(payment_doc.cashdesk)))

        if 'payed_final' in form.changed_data and form.cleaned_data['payed_final'] > 0:
            payment_doc = Cashdesk_detail_income()

            try:
                cashdesk = Cashdesk.objects.get(club_fk=obj.club_fk,status='OPENED')
            except Cashdesk.DoesNotExist:
                messages.error(request,"В момента нямате отворена каса. Моля отворете каса и опитайте пак.")
                obj.deposit = 0
                obj.save()

            payment_doc.order_fk = obj
            payment_doc.amount = obj.payed_final
            payment_doc.note = None
            payment_doc.group_fk = Cashdesk_groups_income.objects.get(name='ПОРЪЧКА',sub_name='ПЛАЩАНЕ')
            payment_doc.cashdesk = cashdesk

            payment_doc.save()

            messages.info(request,"Добавено финално плащане за %.2f лв. Номер:%d, Каса:%s " % (payment_doc.amount,payment_doc.id, str(payment_doc.cashdesk)))

        super(OrderAdmin, self).save_model(request, obj, form, change)

    def take_out_of_store(self, request, obj):
        ########################################################
        # if Article is missing from ArticleStore -print error and abort save
        if obj.store_status:
            messages.error(request,"Поръчката вече е изписана" )

        checked = True
        for ord in obj.orderdetail_set.all():
            try:
                artstore = ArticleStore.objects.get(club_fk = obj.club_fk, article_fk = ord.article_fk)
            except ArticleStore.DoesNotExist:
                messages.info(request,"За артикул %s няма запис в склада. Моля извършете доставка или трансфер." % (str(ord.article_fk),) )
                checked = False
                continue

            if  artstore.cnt - artstore.cnt_bl < ord.cnt:
                messages.info(request,"Няма достатъчна наличност в склада за %s. налични:%d, блокирани:%d, не достигат: %d" % (str(ord.article_fk),artstore.cnt,artstore.cnt_bl, ord.cnt - (artstore.cnt - artstore.cnt_bl) ) )
                checked = False

        if checked:

            #########################################################
            # add record to protocols

            stock_doc = stock_receipt_protocol()
            stock_doc.order_fk = obj
            stock_doc.club_fk = obj.club_fk
            stock_doc.receipt_date = datetime.now()
            stock_doc.type = 'ORDER'
            stock_doc.note = 'Протокол към поръчка Номер %d Дата:%s' % (obj.id,obj.rec_date)
            stock_doc.closed = True
            stock_doc.save()

            #########################################################
            # add each order article as stock delivery detail within the newly created protocol
            for ord in obj.orderdetail_set.all():

                # modify Article Store entry by sustracting quantity
                artstore = ArticleStore.objects.get(club_fk = obj.club_fk, article_fk = ord.article_fk)

                #substract from artstore
                artstore.cnt = artstore.cnt - ord.cnt
                artstore.save()

                stock_del = stock_delivery_detail()
                stock_del.stock_protocol_fk = stock_doc
                stock_del.article_store_fk = artstore
                stock_del.orderdetail_fk = ord
                stock_del.cnt = ord.cnt
                stock_del.save()

            messages.info(request,"Добавен е протокол за изписване от склада. Номер:%d" % (stock_doc.id, ) )



            obj.store_status = True
            obj.save()
        else:

            messages.error(request,"Не е добавен е протокол за изписване от склада" )

    take_out_of_store.label = "Изписване"  # optional
    take_out_of_store.short_description = "Изписване от слкада"  # optional

    change_actions = ('take_out_of_store', )

admin.site.register(Order, OrderAdmin)


class SaloonAdmin(CompareVersionAdmin):
    fields = ('club_fk', 'name','default')

admin.site.register(Saloon, SaloonAdmin)


class TimesAdmin(admin.ModelAdmin):
    fields = ('weekday', 'time_slot','time', 'time_end',)
    list_display = ('id', 'weekday', 'time_slot','time', 'time_end',)
    list_editable = ('weekday', 'time_slot','time', 'time_end',)
    ordering = ('weekday', 'time_slot')
    list_per_page = 100

admin.site.register(Times, TimesAdmin)


class SupplierAdmin(admin.ModelAdmin):
    fields = ('name',)
admin.site.register(Supplier, SupplierAdmin)


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


# class Cashdesk_detail_income_inline_add(admin.TabularInline):
#     model = Cashdesk_detail_income
#
#     readonly_fields = ('order_fk',)
#
#     extra = 1
#     can_delete = False
#     verbose_name = ''
#     verbose_name_plural = ''
#
#     def has_change_permission(self, request, obj=None):
#         return False


class Cashdesk_detail_expense_inline(admin.TabularInline):
    model = Cashdesk_detail_expense
    fields = ('group_fk', 'note', 'amount', 'delivery_fk','transfer_club_fk')
    readonly_fields = ('group_fk', 'note', 'amount', 'delivery_fk','transfer_club_fk')
    extra = 0
    can_delete = False

    def has_add_permission(self, request, obj=None):
            return False


# class Cashdesk_detail_expense_inline_add(admin.TabularInline):
#     model = Cashdesk_detail_expense
#
#     readonly_fields = ('delivery_fk',)
#
#     extra = 1
#     can_delete = False
#     verbose_name = ''
#     verbose_name_plural = ''
#
#     def has_change_permission(self, request, obj=None):
#         return False


class Cashdesk_groups_incomeAdmin(admin.ModelAdmin):
    fields = ('name', 'sub_name',)
    list_display = ('name', 'sub_name',)

admin.site.register(Cashdesk_groups_income, Cashdesk_groups_incomeAdmin)

# class Cashdesk_detail_incomeForm(ModelForm):
#     def clean_transfer_club_fk(self):
#         form_data = self.cleaned_data
#         if 'transfer_club_fk' in form_data and form_data['club_fk'] == form_data['transfer_club_fk']:
#             raise ValidationError("Моля изберете различен обект, към който да се извърши трансфера")
#         return form_data['transfer_club_fk']

class Cashdesk_Groups__expenseAdmin(admin.ModelAdmin):
    fields = ('name', 'sub_name',)
    list_display = ('name', 'sub_name',)

admin.site.register(Cashdesk_groups_expense, Cashdesk_Groups__expenseAdmin)


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


class stock_delivery_detail_inline(admin.TabularInline):
    model = stock_delivery_detail
    fields = ('article_store_fk', 'cnt')
    readonly_fields = ()
    extra = 5

    raw_id_fields = ("article_store_fk",)

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.closed:
            return self.fields
        return self.readonly_fields

    def get_extra(self, request, obj=None, **kwargs):
        if obj and obj.closed:
            return 0
        return self.extra

    def get_max_num(self, request, obj=None, **kwargs):
        if obj and obj.closed:
            return 0
        return self.max_num

    def has_delete_permission(self, request, obj=None):
        if obj and obj.closed:
            return False
        return True


class stock_acceptance_detail_inline(admin.TabularInline):
    model = stock_acceptance_detail
    fields = ('article_store_fk', 'cnt')
    readonly_fields = ()
    extra = 5

    raw_id_fields = ("article_store_fk",)

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.closed:
            return self.fields
        return self.readonly_fields

    def get_extra(self, request, obj=None, **kwargs):
        if obj and obj.closed:
            return 0
        return self.extra

    def get_max_num(self, request, obj=None, **kwargs):
        if obj and obj.closed:
            return 0
        return self.max_num

    def has_delete_permission(self, request, obj=None):
        if obj and obj.closed:
            return False
        return True


class stock_receipt_protocolForm(ModelForm):
    def clean_transfer_club_fk(self):
        form_data = self.cleaned_data
        if 'transfer_club_fk' in form_data and form_data['club_fk'] == form_data['transfer_club_fk']:
            raise ValidationError("Моля изберете различен обект, към който да се извърши трансфера")
        return form_data['transfer_club_fk']


class stock_receipt_protocolAdmin(DjangoObjectActions, CompareVersionAdmin):

    list_display =('type','id','receipt_date', 'club_fk','transfer_club_fk' )
    readonly_fields = ('id','order_fk' ,'delivery_fk','transfer_fk','receipt_date', 'closed')
    form = stock_receipt_protocolForm
    fields = ('cashdesk', 'group_fk','note','amount','transfer_club_fk')
    list_filter = ('receipt_date','type','club_fk','closed')
    search_fields = ('note','group_fk__name','group_fk__sub_name')
    list_per_page = 50
    date_hierarchy = "receipt_date"

    def get_fields(self, request, obj=None):
        if obj and obj.type == 'ORDER':
            return 'id', 'type', 'club_fk', 'receipt_date', 'order_fk', 'closed', 'note',
        if obj and obj.type == 'DELIVERY':
            return 'id', 'type', 'club_fk', 'receipt_date', 'delivery_fk','closed', 'note',
        if obj and obj.type in  ('EXPDELIVERY','EXPEDITION'):
            return 'id', 'type', 'club_fk', 'receipt_date', 'transfer_fk','transfer_club_fk','closed', 'note',

        return 'id', 'type', 'club_fk', 'receipt_date','closed','note',

    def get_form(self, request, obj=None, **kwargs):

        form = super(stock_receipt_protocolAdmin, self).get_form(request, obj,**kwargs)

        if not obj:
            # remove ORDER and DELIVERY, since they are only added automatically
            form.base_fields['type'].choices = stock_receipt_protocol.MANUAL_TYPES

        # if editing (obj will be filled in with the existing model)
        if obj and not obj.closed:
            form.base_fields['type'].disabled = True
            form.base_fields['club_fk'].disabled = True

            if obj.transfer_club_fk:
                form.base_fields['transfer_club_fk'].disabled = True

        # if club is specified for the current user (in the user model), do not allow choosing another club
        if request.user.employee.club_fk and not obj.closed:
            form.base_fields['club_fk'].initial = request.user.employee.club_fk
            form.base_fields['club_fk'].widget.attrs.update({'readonly':'True','style':'pointer-events:none'})  # simulates readonly on the browser with the help of css

        return form

    inlines = [
        stock_delivery_detail_inline,
        stock_acceptance_detail_inline,
    ]

    def get_inline_instances(self, request, obj=None):
        inline_instances = super(stock_receipt_protocolAdmin, self).get_inline_instances(request,obj)

        # for new instances do not allow inlines - this way the protocol type will be initially set, then after
        # save and reload the appropriate inline types will be allowed only
        if not obj:
            return []

        # remove specific inlines that are not applicable depending on protocol type

        fixed_inline_instances = []
        for inline in inline_instances:
            if obj and obj.type in ('ORDER','LATEORD','SCRAP','INTERNAL','EXPEDITION') and isinstance(inline, stock_acceptance_detail_inline):
                continue
            if obj and obj.type in ('DELIVERY','CORDELIVERY','EXPDELIVERY') and isinstance(inline, stock_delivery_detail_inline):
                continue
            fixed_inline_instances.append(inline)

        return fixed_inline_instances

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.closed:
            return self.get_fields(request, obj)
        return self.readonly_fields

    def stock_receipt_protocol_close(self, request, obj):

        # check if closed
        if obj.closed:
            messages.error(request,"Този протокол вече е приключен.")
            return

        ########################################################
        # check Article Store availability

        # if Article is missing from ArticleStore -print error and abort
        checked = True
        for stock_dev in obj.stock_delivery_detail_set.all():
            if stock_dev.article_store_fk.cnt - nvl(stock_dev.article_store_fk.cnt_bl,0) < stock_dev.cnt:
                messages.info(request,"Няма достатъчна наличност в склада за %s. налични:%d, блокирани:%d, не достигат: %d" % (str(stock_dev.article_store_fk.article_fk),stock_dev.article_store_fk.cnt,stock_dev.article_store_fk.cnt_bl, stock_dev.cnt - (stock_dev.article_store_fk.cnt - stock_dev.article_store_fk.cnt_bl) ) )
                checked = False

        # if transfer create a mirror protocol in other club
        if checked:

            #########################################################
            # add/substract quantities to ArticleStore
            for stock_dev in obj.stock_delivery_detail_set.all():
                # modify Article Store entry by sustracting quantity
                stock_dev.article_store_fk.cnt = stock_dev.article_store_fk.cnt - stock_dev.cnt
                stock_dev.article_store_fk.save()


            for stock_dev in obj.stock_acceptance_detail_set.all():
                # modify Article Store entry by adding quantity
                stock_dev.article_store_fk.cnt = stock_dev.article_store_fk.cnt + stock_dev.cnt
                stock_dev.article_store_fk.save()

            if obj.type == 'EXPEDITION':

                #########################################################
                # add record to protocols

                stock_doc = stock_receipt_protocol()
                stock_doc.transfer_fk = obj
                stock_doc.club_fk = obj.transfer_club_fk
                stock_doc.transfer_club_fk = obj.club_fk
                stock_doc.receipt_date = datetime.now()
                stock_doc.type = 'EXPDELIVERY'
                stock_doc.note = 'Протокол към трансфер Номер %d' % (obj.id,)
                stock_doc.closed = True
                stock_doc.save()

                obj.transfer_fk = stock_doc

                #########################################################
                # add each order article as stock delivery detail within the newly created protocol
                for stock_dev in obj.stock_delivery_detail_set.all():

                    # lookup store from the other side
                    try:
                        artstore = ArticleStore.objects.get(club_fk = obj.transfer_club_fk, article_fk = stock_dev.article_store_fk.article_fk)
                    except ArticleStore.DoesNotExist:
                        artstore = ArticleStore()
                        artstore.user = request.user
                        artstore.club_fk = obj.transfer_club_fk
                        artstore.article_fk = stock_dev.article_store_fk.article_fk
                        artstore.cnt = 0
                        artstore.cnt_min = 0
                        artstore.cnt_bl = 0


                    artstore.cnt +=  stock_dev.cnt
                    artstore.save()

                    #########################################################
                    # create a corresponding acceptance detail
                    stock_acc = stock_acceptance_detail()
                    stock_acc.stock_protocol_fk = stock_doc
                    stock_acc.article_store_fk = artstore
                    stock_acc.cnt = stock_dev.cnt
                    stock_acc.save()

                messages.info(request,"Добавен е протокол за трансфер от склада. от номер:%d към номер:%d" % (obj.id,stock_doc.id, ) )

            obj.closed = True
            obj.save()
        else:

            messages.error(request,"Не е приключен е протокол за изписване от склада" )


        #todo: validate for negative quantities


    stock_receipt_protocol_close.label = "Приключване"  # optional
    stock_receipt_protocol_close.short_description = "Приключване на протокол"  # optional

    change_actions = ('stock_receipt_protocol_close', )


admin.site.register(stock_receipt_protocol, stock_receipt_protocolAdmin)