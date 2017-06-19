import json

from django import forms
from django.http import HttpResponse
from datetime import datetime, time

from django.shortcuts import render_to_response
from django.template import RequestContext

from nomenclature.models import Club
from order.models import Order


def calendar_order_data(request):

    start_parameter = request.GET['start']
    end_parameter = request.GET['end']

    start_date = datetime.strptime(start_parameter,'%Y-%m-%d')
    end_date = datetime.strptime(end_parameter,'%Y-%m-%d')
    club_id = request.GET['club_id']

    orders=Order.objects.filter(rec_date__gte=start_date,rec_date__lte =end_date,club_fk = club_id).exclude(status='CANCELED')

    json_ins = []
    for order in orders:
        inp = {}

        inp['title'] = 'order:' + str(order)
        inp['start'] = datetime.strftime(order.rec_date,'%Y-%m-%d')+ 'T' + time.strftime(order.rec_time,'%H:%M')
        inp['end'] = datetime.strftime(order.rec_date,'%Y-%m-%d')+ 'T' + time.strftime(order.rec_time_end,'%H:%M')
        inp['id'] = order.id
        inp['url'] = '/admin/order/order/'+str(order.id)+'/change/'
        inp['textColor'] = 'black'

        if order.status == 'REQUESTED':
            inp['color'] = '#85e085'
        elif order.status == 'CONFIRMED':
            inp['color'] = '#ffff99'
        elif order.status == 'ORDERED':
            inp['color'] = '#ff8566'
        elif order.status == 'CANCELED':
            inp['color'] = '#00ff00'
        else:
            inp['color'] = '#85e085'

        json_ins.append(inp)

    json_txt = json.dumps(json_ins)
    return HttpResponse (json_txt)

def order_resize(request):
    pass

def order_move(request):
    pass

class Form_Club(forms.Form):
    club_field = forms.ModelChoiceField(label='Клуб',queryset=Club.objects.all())

def calendar_view(request):
    context = RequestContext(request)
    form_club = Form_Club()
    if request.user.employee.club_fk:
        form_club.fields['club_field'].initial = request.user.employee.club_fk
        form_club.fields['club_field'].widget.attrs.update({'readonly':'True','style':'pointer-events:none'})  # simulates readonly on the browser with the help of css
    calendar_data={}
    calendar_data['form'] = form_club
    return render_to_response("calendar.html", calendar_data,context)
# 'form':form