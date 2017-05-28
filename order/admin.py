from datetime import datetime, timedelta, time
from decimal import Decimal
from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.contrib.admin.utils import flatten
from django.core.exceptions import ValidationError
from django.forms import ModelForm, DateField, TimeField
from django.contrib import messages
from django.core.urlresolvers import reverse_lazy

from cashdesk.models import Cashdesk_detail_income, Cashdesk
from clever_select_enhanced.form_fields import ChainedModelChoiceField
from datetimewidget.widgets import DateWidget, TimeWidget
from nomenclature.models import ArticleGroup, Saloon, Cashdesk_groups_income
from order.models import *
from clever_select_enhanced.forms import ChainedChoicesModelForm
from clever_select_enhanced.clever_txt_field import ChainedNumberInputField

from django_object_actions import DjangoObjectActions

from ostrovaweb.utils import nvl
from store.models import ArticleStore, stock_delivery_detail, stock_receipt_protocol


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

    rec_date = DateField(label="Дата на р.д.", required=True, widget=DateWidget(
        options = {
            'format': 'yyyy-mm-dd',
            'startDate': (datetime.now()+ timedelta(days=1)).strftime('%Y-%m-%d'),
            'initialDate': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),
            'minView':2,
            #        'hoursDisabled': '"0,1,2,3,4,5,6,7,8,20,21,22,23"',
            'language':'bg'
        }
    ))
    rec_time = TimeField(label="Начало",  required=True, widget=TimeWidget(
        options = {
            'format': 'hh:ii',
            'minView':0,
            'maxView':2,
            'minuteStep':15,
            'hoursDisabled': '"0,1,2,3,4,5,6,7,8,20,21,22,23"',
            'language':'bg'
        }
    ))
    rec_time_end = TimeField(label="Край",  required=True, widget=TimeWidget(
        options = {
            'format': 'hh:ii',
            'minView':0,
            'maxView':2,
            'minuteStep':15,
            'hoursDisabled': '"0,1,2,3,4,5,6,7,8,20,21,22,23"',
            'language':'bg'
        }
    ))
    def clean(self):

        # rec_time triabva da e po-malko ot rec_time_end
        if self.cleaned_data['rec_time'] > self.cleaned_data['rec_time_end']:
                raise ValidationError("Моля изберете по-малък начален час от крайният")

        if self.cleaned_data['rec_time'].hour < 10:
            raise ValidationError("Моля изберете по-голям начален час от 10 часа")

        if self.cleaned_data['rec_time_end'].hour > 21:
            raise ValidationError("Моля изберете по-малък начален час от 21 часа")

        self.cleaned_data['rec_time'] = time.strftime(self.cleaned_data ['rec_time'],'%H:%M' )
        self.cleaned_data['rec_time_end'] = time.strftime(self.cleaned_data ['rec_time_end'],'%H:%M' )

        # da se proveri (sas filter ot bazata) dali ima veche rojden den za tazi data i chas i klub
        orders = Order.objects.filter(rec_date= self.cleaned_data['rec_date'], club_fk=self.cleaned_data['club_fk']).exclude(id=self.instance.id).exclude(status='CANCELED')
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
            # 'rec_time': AdminTimeWidget({'format': '%H:%M'}),
            # 'rec_time_end': AdminTimeWidget,
        }

class OrderAdmin(DjangoObjectActions, ModelAdmin):

    change_list_template = "admin/order/order/change_list.html"
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
            else:
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
            else:
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
            else:
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