from datetime import datetime, timedelta

from decimal import Decimal
from django import forms
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template import RequestContext
from paypal.standard.forms import PayPalPaymentsForm

from datetimewidget.widgets import DateTimeWidget, DateWidget, TimeWidget
from nomenclature.models import Club, Saloon
from order.models import Order
from ostrovaweb.utils import nvl


class Form_SiteOrder(forms.Form):
    parent = forms.CharField(label='Родител',  required=True, max_length=240)
    phone = forms.CharField(label="Телефон",  required=True, max_length=100)
    child = forms.CharField(label="Дете",max_length=200,required=False)
    age = forms.IntegerField(label="Години",required=False)

    rec_date = forms.DateField(label="Дата на р.д.", required=True, widget=DateWidget(
        options = {
        'format': 'yyyy-mm-dd',
        'startDate': (datetime.now()+ timedelta(days=1)).strftime('%Y-%m-%d'),
        'initialDate': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),
        'minView':2,
#        'hoursDisabled': '"0,1,2,3,4,5,6,7,8,20,21,22,23"',
        'language':'bg'
        }
    ))
    rec_time = forms.TimeField(label="Начало",  required=True, widget=TimeWidget(
        options = {
            'format': 'hh:ii',
            'minView':0,
            'maxView':2,
            'minuteStep':15,
            'hoursDisabled': '"0,1,2,3,4,5,6,7,8,20,21,22,23"',
            'language':'bg'
        }
    ))
    rec_time_end = forms.TimeField(label="Край",  required=True, widget=TimeWidget(
        options = {
            'format': 'hh:ii',
            'minView':0,
            'maxView':2,
            'minuteStep':15,
            'hoursDisabled': '"0,1,2,3,4,5,6,7,8,20,21,22,23"',
            'language':'bg'
        }
    ))
    child_count = forms.IntegerField(label="Брой деца",required=False)
    adult_count = forms.IntegerField(label="Брой възрастни",required=False)

    club_field = forms.ModelChoiceField(label='Клуб', required=False, queryset=Club.objects.all())

    def clean(self):
        if 'rec_time' in self.cleaned_data and 'rec_time_end' in self.cleaned_data:
            if self.cleaned_data['rec_time'] >= self.cleaned_data['rec_time_end']:
                raise ValidationError("Моля изберете по-малък начален час от крайният")

        return self.cleaned_data


def index(request):
    context = RequestContext(request)

    template_data = {}
    template_data['user'] = request.user

    return render_to_response("index.html", template_data,context)


@login_required
def siteorder_list(request):
    context = RequestContext(request)

    orders = Order.objects.filter(email=request.user.email)

    template_data={}
    template_data['orders'] = orders
    template_data['user'] = request.user
    return render_to_response("siteorder_list.html", template_data,context)


@login_required
def siteorder_view(request):
    context = RequestContext(request)
    form_siteorder = Form_SiteOrder()

    template_data={}
    template_data['form'] = form_siteorder
    template_data['user'] = request.user
    return render_to_response("siteorder.html", template_data,context)


@login_required
def siteorder_confirm_view(request):
    context = RequestContext(request)
    form_siteorder = Form_SiteOrder(request.POST)

    # todo: validate harder
    if form_siteorder.is_valid():
         order = Order()
         order.rec_date = form_siteorder.cleaned_data['rec_date']
         order.rec_time = form_siteorder.cleaned_data['rec_time']
         order.rec_time_end = form_siteorder.cleaned_data['rec_time_end']
         order.phone = form_siteorder.cleaned_data['phone']
         order.parent = form_siteorder.cleaned_data['parent']
         order.child = form_siteorder.cleaned_data['child']
         order.age = form_siteorder.cleaned_data['age']
         order.child_count = form_siteorder.cleaned_data['child_count']
         order.adult_count = form_siteorder.cleaned_data['adult_count']
         order.email = request.user.email
         order.status = 'REQUESTED'
         order.user = request.user
         order.club_fk =  form_siteorder.cleaned_data['club_field']

         if form_siteorder.cleaned_data['club_field'] is not None:
            order.saloon_fk = Saloon.objects.get(club_fk=form_siteorder.cleaned_data['club_field'], default=True)

         order.save()
    else:
        template_data={}
        template_data['form'] = form_siteorder
        template_data['user'] = request.user
        return render_to_response("siteorder.html", template_data,context)

    template_data={}
    template_data['form'] = form_siteorder
    template_data['user'] = request.user
    return render_to_response("siteorder_confirm.html", template_data, context)


@login_required
def siteorder_pay_deposit(request):
    order_id = request.GET['id']

    order = Order.objects.get(id=order_id)

    amount = str(50.0 * 0.572310)
    text = "Капаро за парти"

    context = RequestContext(request)
    paypal_dict = {
        "business": "putbul_lady-facilitator@abv.bg",
        "amount": amount,
        "item_name": text,
        "invoice": "order-deposit" + str(order.id),
        "notify_url": "https://ostrovaweb.herokuapp.com" + reverse('paypal-ipn'),
        "return_url": "https://ostrovaweb.herokuapp.com/accounts/profile/",
        "cancel_return": "https://ostrovaweb.herokuapp.com/pay-cancel",
    }

    # Create the instance.
    form = PayPalPaymentsForm(initial=paypal_dict)

    template_data={}
    template_data['form'] = form
    template_data['user'] = request.user
    template_data['payment_data'] = [
        ['Сума', "%.2f" % float(amount),],
        ['Основание', text],
    ]
    return render_to_response("siteorder_paypal.html", template_data, context)


@login_required
def siteorder_pay_final(request):
    order_id = request.GET['id']

    order = Order.objects.get(id=order_id)

    amount = str(nvl(order.dueAmount_int(),0) * Decimal(0.572310))
    text = "Финално плащане за парти"

    context = RequestContext(request)
    paypal_dict = {
        "business": "putbul_lady-facilitator@abv.bg",
        "amount": amount,
        "item_name": text,
        "invoice": "order-final" + str(order.id),
        "notify_url": "https://ostrovaweb.herokuapp.com" + reverse('paypal-ipn'),
        "return_url": "https://ostrovaweb.herokuapp.com/accounts/profile/",
        "cancel_return": "https://ostrovaweb.herokuapp.com/pay-cancel",
    }

    # Create the instance.
    form = PayPalPaymentsForm(initial=paypal_dict)

    template_data={}
    template_data['form'] = form
    template_data['user'] = request.user
    template_data['payment_data'] = [
        ['Сума', "%.2f" % float(amount),],
        ['Основание', text],
    ]
    return render_to_response("siteorder_paypal.html", template_data, context)
