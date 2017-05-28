from django import template
from django.core.urlresolvers import reverse

#from casyscmsApp.preserveChangeListFiltersInSession import restoreFilterSpecsOnUrl


register = template.Library()

@register.simple_tag
def get_verbose_field_name(instance, field_name):
    """
    Returns verbose_name for a field or field if missing.
    """
    verbose_name = field_name
    try:
        verbose_name = instance._meta.get_field(field_name).verbose_name.title()
    except:
        pass
    return verbose_name

# @register.simple_tag
# def restore_filter_specs_on_admin_url(instance, value, request):
#     """
#         1. added filter preservation - through a middleware request processor and by logging into a map all requests parameters in user's session
#         2. then on certain places - namely changelist redirects fetch the stored url prams and glue them to the redirect url - those are actually the last selected filter params of changelist itself
#         3. added a template tag in cs_tags  to wrap around change list url rendered in templates
#     """
#     return restoreFilterSpecsOnUrl(request, reverse(value))