from django.apps import AppConfig
from paypal.standard.ipn.signals import valid_ipn_received

from siteorder.siteorder import show_me_the_money


class OrderConfig(AppConfig):
    name = 'order'
    verbose_name = 'Поръчки за парти'

    def ready(self):
        valid_ipn_received.connect(show_me_the_money)