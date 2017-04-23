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
from django.conf.urls import url, include
from django.contrib import admin

from ostrovaCalendar.article_views import ArticleAjaxChainedView

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    url(r'^admin/ajax/article-chained/$', ArticleAjaxChainedView.as_view(), name='article_ajax_chained_models'),

    #url(r'^fullcalendar/', TemplateView.as_view(template_name="calendar.html"), name='fullcalendar'),
    # url(r'^schedule/', include('schedule.urls')),

    url(r'^report_builder/', include('report_builder.urls')),
    #url(r'^explorer/', include('explorer.urls')),
]
