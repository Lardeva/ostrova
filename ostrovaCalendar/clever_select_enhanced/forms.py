from ostrovaweb.utils import nvl

__author__ = 'Erik Telepovsky'

import json

from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import EMPTY_VALUES
from django.db import models

from ostrovaCalendar.clever_select_enhanced.form_fields import ChainedChoiceField, ChainedModelChoiceField
from ostrovaCalendar.clever_select_enhanced.testclient import TestClient


class ChainedChoicesMixin(object):
    """
    Form Mixin to be used with ChainedChoicesForm and ChainedChoicesModelForm.
    It loads the options when there is already an instance or initial data.
    """
    user = None
    prefix = None
    fields = []
    chained_fields_names = []
    chained_model_fields_names = []

    def init_chained_choices(self, *args, **kwargs):
        self.chained_fields_names = self.get_fields_names_by_type(ChainedChoiceField)
        self.chained_model_fields_names = self.get_fields_names_by_type(ChainedModelChoiceField)
        self.user = kwargs.get('user', self.user)

        if kwargs.get('data', None) is not None:
            self.set_choices_via_ajax(kwargs['data'])

        elif len(args) > 0 and args[0] not in EMPTY_VALUES:
            self.set_choices_via_ajax(args[0])

        elif kwargs.get('instance', None) is not None:
            oldest_parent_field_names = list(set(self.get_oldest_parent_field_names()))
            youngest_child_names = list(set(self.get_youngest_children_field_names()))

            for youngest_child_name in youngest_child_names:
                self.find_instance_attr(kwargs['instance'], youngest_child_name)

            for oldest_parent_field_name in oldest_parent_field_names:
                try:
                    self.fields[oldest_parent_field_name].initial = getattr(self.instance, '%s' % oldest_parent_field_name)
                except AttributeError:
                    pass

            self.set_choices_via_ajax()

        elif 'initial' in kwargs and kwargs['initial'] not in EMPTY_VALUES:
            self.set_choices_via_ajax(kwargs['initial'], is_initial=True)
        else:
            for field_name in self.chained_fields_names + self.chained_model_fields_names:
                empty_label = self.fields[field_name].empty_label
                self.fields[field_name].choices = [('', empty_label)]

    def set_choices_via_ajax(self, kwargs=None, is_initial=False):
        for field_name in self.chained_fields_names + self.chained_model_fields_names:
            field = self.fields[field_name]
            try:
                c = TestClient()

                try:
                    if self.user:
                        c.login_user(self.user)
                except AttributeError:
                    pass

                additional_related_field = None
                additional_related_value = None
                if kwargs is not None:
                    # initial data do not have any prefix
                    if self.prefix in EMPTY_VALUES or is_initial:
                        parent_value = kwargs.get(field.parent_field, None)
                        field_value = kwargs.get(field_name, None)

                        if hasattr(field, 'additional_related_field'):
                            additional_related_field = field.additional_related_field
                            if '__' in additional_related_field:
                                # handle reference from inline field
                                additional_related_value = kwargs.get('%s' % (field.additional_related_field.split('__')[-1]), None)
                            else:
                                # handle normal reference
                                additional_related_value = kwargs.get(field.additional_related_field, None)
                    else:
                        field_value = kwargs.get('%s-%s' % (self.prefix, field_name), None)

                        if field.inline_fk_to_master:
                            # handle reference from inline field
                            parent_value = kwargs.get('%s' % field.parent_field, None)
                        else:
                            # handle normal inlined (or prefixed) reference
                            parent_value = kwargs.get('%s-%s' % (self.prefix, field.parent_field), None)

                        if hasattr(field, 'additional_related_field') and field.additional_related_field:
                            additional_related_field = field.additional_related_field

                            # a rather clumsy way to support master field lookup
                            if '__' in additional_related_field:
                                # handle reference from inline field
                                additional_related_value = kwargs.get('%s' % (field.additional_related_field.split('__')[-1]), None)
                            else:
                                # handle normal inlined (or prefixed) reference
                                additional_related_value = kwargs.get('%s-%s' % (self.prefix, field.additional_related_field), None)

                else:
                    field_value = getattr(self.instance, '%s' % field_name, None)

                    if field.inline_fk_to_master:
                        # handle reference from inline field
                        parent_value = getattr(self.instance, '%s' % field.inline_fk_to_master, None)
                        parent_value = getattr(parent_value, '%s' % field.parent_field, None)
                    else:
                        # handle normal/inlined reference
                        parent_value = getattr(self.instance, '%s' % field.parent_field, None)

                    if hasattr(field, 'additional_related_field') and field.additional_related_field:
                        additional_related_field = field.additional_related_field

                        # lookup "deep" references of models, split with underscores, following foreign keys
                        obj = self.instance
                        pref_li = additional_related_field.split('__')
                        for x in pref_li:
                            if obj:
                                obj = getattr(obj, '%s' % x, None)

                        additional_related_value = obj


                field.choices = [('', field.empty_label)]

                # check that parent_value is valid
                if parent_value:
                    parent_value = getattr(parent_value, 'pk', parent_value)
                    additional_related_value = getattr(additional_related_value, 'pk', additional_related_value)

                    url = field.ajax_url
                    params = {
                        'field': field_name,
                        'parent_value': parent_value,
                        'field_value': field_value,
                        'add_rel_field': nvl(additional_related_field,''),
                        'add_rel_value': nvl(additional_related_value,'')

                    }
                    data = c.get(url, params)

                    try:
                        field.choices = field.choices + json.loads(data.content.decode('utf-8'))
                    except ValueError:
#                        raise
                        raise ValueError(u'Data returned from ajax request (url=%(url)s, params=%(params)s) could not be deserialized to Python object. %(data)s' % {
                            'url': url,
                            'params': params,
                            'data':str(data.content)
                        })

                field.initial = field_value

            except ObjectDoesNotExist:
                field.choices = ()

    def get_fields_names_by_type(self, type):
        result = []
        for field_name in self.fields:
            field = self.fields[field_name]
            if isinstance(field, type):
                result.append(field_name)
        return result

    def get_parent_fields_names(self):
        result = []
        for field_name in self.fields:
            field = self.fields[field_name]
            if hasattr(field, 'parent_field'):
                result.append(field.parent_field)
        return result

    def get_children_field_names(self, parent_name):
        if parent_name in EMPTY_VALUES:
            return []
        result = []
        for field_name in self.fields:
            field = self.fields[field_name]
            if getattr(field, 'parent_field', None) == parent_name:
                result.append(field_name)
        return result

    def get_chained_fields_names(self):
        chained_fields_names = self.get_fields_names_by_type(ChainedChoiceField)
        chained_model_fields_names = self.get_fields_names_by_type(ChainedModelChoiceField)
        return chained_fields_names + chained_model_fields_names

    def get_oldest_parent_field_names(self):
        chained_fields_names = self.get_fields_names_by_type(ChainedChoiceField)
        chained_model_fields_names = self.get_fields_names_by_type(ChainedModelChoiceField)

        oldest_parent_field_names = []
        for field_name in self.get_parent_fields_names():
            if field_name not in chained_fields_names and field_name not in chained_model_fields_names:
                oldest_parent_field_names.append(field_name)
        return oldest_parent_field_names

    def get_youngest_children_field_names(self):
        result = []
        chained_fields_names = self.get_fields_names_by_type(ChainedChoiceField)
        chained_model_fields_names = self.get_fields_names_by_type(ChainedModelChoiceField)

        for field_name in chained_fields_names + chained_model_fields_names:
            if field_name not in self.get_parent_fields_names():
                result.append(field_name)
        return result

    def find_instance_attr(self, instance, attr_name):
        field = self.fields[attr_name]
        if hasattr(instance, attr_name):
            attribute = getattr(instance, attr_name)
            attr_value = getattr(attribute, 'pk', str(attribute)) if attribute else None
            setattr(self, '%s' % attr_name, attr_value)

            if hasattr(field, 'parent_field'):
                parent_instance = attribute if isinstance(attribute, models.Model) else instance
                self.find_instance_attr(parent_instance, field.parent_field)


class ChainedChoicesForm(forms.Form, ChainedChoicesMixin):
    """
    Form class to be used with ChainedChoiceField and ChainedSelect widget
    If there is request POST data in *args (i.e. form validation was invalid)
    then the options will be loaded when the form is built.
    """
    def __init__(self, language_code=None, *args, **kwargs):
        super(ChainedChoicesForm, self).__init__(*args, **kwargs)
        self.language_code = kwargs.get('language_code', None)
        self.init_chained_choices(*args, **kwargs)

    def is_valid(self):
        if self.language_code:
            # response is not translated to requested language code :/
            # so translation is triggered manually
            from django.utils.translation import activate
            activate(self.language_code)
        return super(ChainedChoicesForm, self).is_valid()


class ChainedChoicesModelForm(forms.ModelForm, ChainedChoicesMixin):
    """
    Form class to be used with ChainedChoiceField and ChainedSelect widget
    If there is already an instance (i.e. editing)
    then the options will be loaded when the form is built.
    """
    def __init__(self,  *args, **kwargs):
        super(ChainedChoicesModelForm, self).__init__(*args, **kwargs)
        #self.language_code = kwargs.get('language_code', None)
        self.init_chained_choices(*args, **kwargs)

    def is_valid(self):
        #        if self.language_code:
        #            # response is not translated to requested language code :/
        #            # so translation is triggered manually
        #            from django.utils.translation import activate
        #            activate(self.language_code)
        return super(ChainedChoicesModelForm, self).is_valid()
