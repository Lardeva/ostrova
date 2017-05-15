from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers   import reverse
from django.forms import BaseInlineFormSet


def nvl(data, val=''):
    if data is None:
        return val
    return data


class AdminURLMixin(object):

    def get_admin_url(self):
        content_type = ContentType.objects.get_for_model(self.__class__)

        return reverse("admin:%s_%s_change" % (
            content_type.app_label,
            content_type.model),
                       args=(self.id,))

class RequiredFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super(RequiredFormSet, self).__init__(*args, **kwargs)
        self.forms[0].empty_permitted = False