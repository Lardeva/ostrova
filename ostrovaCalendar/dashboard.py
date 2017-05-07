from controlcenter import Dashboard, widgets
from ostrovaCalendar.models import *

class ModelItemList(widgets.ItemList):
    model = Order
    list_display = ('rec_date', 'club_fk', 'rec_time', 'parent', 'child', 'locked', 'payed_final',)

class MyDashboard(Dashboard):
    widgets = (
        ModelItemList,
    )