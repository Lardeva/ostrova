from ostrovaCalendar.clever_select_enhanced.views import ChainedSelectChoicesView
from ostrovaCalendar.models import Saloon


class SaloonAjaxClubChainedView(ChainedSelectChoicesView):


    def get_choices(self):
        vals_list = []
        ids_list = []

        if self.field.endswith('saloon_fk'):
            saloon = Saloon.objects.filter(club_fk=self.parent_value)

            vals_list = [x.name for x in saloon]
            ids_list = [x.id for x in saloon]


        return tuple(zip(ids_list, vals_list))

