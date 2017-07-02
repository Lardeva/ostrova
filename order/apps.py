from django.apps import AppConfig

class OrderConfig(AppConfig):
    name = 'order'
    verbose_name = 'Поръчки за парти'

    def ready(self):

        from paypal.standard.ipn.signals import valid_ipn_received
        from siteorder.siteorder import show_me_the_money

        valid_ipn_received.connect(show_me_the_money)