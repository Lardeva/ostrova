"""ostrovaweb URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from controlcenter.views import controlcenter
from django.conf.urls import url, include
from django.contrib import admin
from django.views.generic import TemplateView

from ostrovaCalendar import article_views
from ostrovaCalendar import calendarview
from ostrovaCalendar.article_views import ArticleAjaxChainedView, ArticleAjaxOrderChainedView

#from ostrovaCalendar.orderview import get_order_list, calendar_view

#from model_report import report
#report.autodiscover()
from ostrovaCalendar import reports
from ostrovaCalendar.clubview import SaloonAjaxClubChainedView
from ostrovaCalendar.siteorder import siteorder

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    url(r'^fullcalendar/', calendarview.calendar_view, name='fullcalendar'),
    url(r'^calendar_orders_feed/', calendarview.calendar_order_data, name='calendar_orders_feed'),


    url(r'^admin/ajax/saloon-chained/$', SaloonAjaxClubChainedView.as_view(), name='saloon_ajax_chained_models'),
    url(r'^admin/ajax/article-chained/$', ArticleAjaxChainedView.as_view(), name='article_ajax_chained_models'),
    url(r'^admin/ajax/article-chained-order/$', ArticleAjaxOrderChainedView.as_view(), name='article_ajax_chained_order_models'),

    url(r'^article_name_lookup/', article_views.article_name_lookup, name='article_name_lookup'),

    url(r'^select2/', include('django_select2.urls')),

    #url(r'^admin/dashboard/', controlcenter.urls),
    #url(r'^report_builder/', include('report_builder.urls')),
    #url(r'', include('model_report.urls')),
#    url(r'^accounts/', include('allauth.urls')),

    url(r'^$', siteorder.index, name='index'),
    url(r'^siteorder/', siteorder.siteorder_view, name='siteorder'),
    url(r'^siteorderconfirm/', siteorder.siteorder_confirm_view, name='siteorder_confirm_view'),
    url(r'^accounts/profile/', siteorder.siteorder_list, name='siteorder_list'),
    url(r'^siteorderpaydeposit/', siteorder.siteorder_pay_deposit, name='siteorder_pay_deposit'),
    url(r'^siteorderpayfinal/', siteorder.siteorder_pay_final, name='siteorder_pay_final'),

    url(r'^paypal/', include('paypal.standard.ipn.urls')),

    #url(r'^accounts/', include('registration.backends.default.urls')),
    url(r'^accounts/', include('registration.backends.simple.urls')),

    url(r'^cubesviewer/', include('cubesviewer.urls')),

]
