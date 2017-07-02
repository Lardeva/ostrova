from django.apps import AppConfig

class OrderConfig(AppConfig):
    name = 'order'
    verbose_name = 'Поръчки за парти'

    # def ready(self):
    #
    #     from paypal.standard.ipn.signals import valid_ipn_received
    #     from siteorder.siteorder import show_me_the_money
    #     import logging
    #     from django.db.models.signals import pre_save, pre_init, pre_delete, post_save, post_delete, post_init
    #
    #     valid_ipn_received.connect(show_me_the_money)
    #
    #     logging.error('shhh')
    #     for signal in [pre_save, pre_init, pre_delete, post_save, post_delete, post_init]:
    #         # print a List of connected listeners
    #         logging.error(str(signal.receivers))