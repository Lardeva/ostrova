from django.core import validators
from django.core.exceptions import ValidationError
from django.forms import ChoiceField
from django.forms.models import ModelChoiceField

from ostrovaCalendar.clever_select_enhanced.widgets import ChainedSelect


class ChainedChoiceField(ChoiceField):
    def __init__(self, parent_field, ajax_url, choices=None, empty_label='--------', *args, **kwargs):

        self.parent_field = parent_field
        self.ajax_url = ajax_url
        self.choices = choices or (('', empty_label), )
        self.empty_label = empty_label

        defaults = {
            'widget': ChainedSelect(parent_field=parent_field, ajax_url=ajax_url, attrs={'empty_label': empty_label}),
        }
        defaults.update(kwargs)

        super(ChainedChoiceField, self).__init__(choices=self.choices, *args, **defaults)

    def valid_value(self, value):
        """Dynamic choices so just return True for now"""
        return True


class ChainedModelChoiceField(ModelChoiceField):
    def __init__(self, parent_field, ajax_url, model, empty_label='--------', inline_fk_to_master = None, field_prefix = None, additional_related_field=None, additional_related_field_prefix = None, *args, **kwargs):

        self.parent_field = parent_field
        self.ajax_url = ajax_url
        self.model = model
        #self.queryset = model.objects.all()  # Large querysets could take long time to load all values (django-cities)
        self.queryset = model.objects.none()
        self.empty_label = empty_label
        self.inline_fk_to_master = inline_fk_to_master
        self.additional_related_field = additional_related_field

        # if field is referencing from inline to master record, then field prefix should not be the inline field form, but rather the simplier
        # id_<field name>. The ChainedSelect will account this.

        if inline_fk_to_master and not field_prefix:
            field_prefix = 'id_'

        if additional_related_field and '__' in additional_related_field:
            # if "deep" references of models used for related fields, take only the last part to reference the form field
            additional_related_field = additional_related_field.split('__')[-1]
            if not additional_related_field_prefix:
                additional_related_field_prefix = 'id_'

        defaults = {
            'widget': ChainedSelect(parent_field=parent_field, ajax_url=ajax_url,
                                    field_prefix = field_prefix,
                                    additional_related_field_prefix = additional_related_field_prefix,
                                    additional_related_field  = additional_related_field,
                                    attrs={'empty_label': empty_label, }),
        }
        defaults.update(kwargs)

        super(ChainedModelChoiceField, self).__init__(queryset=self.queryset, empty_label=empty_label, *args, **defaults)

    def valid_value(self, value):
        """Dynamic choices so just return True for now"""
        return True

    def to_python(self, value):
        empty_values = getattr(self, 'empty_values', list(validators.EMPTY_VALUES))
        if value in empty_values:
            return None
        try:
            key = self.to_field_name or 'pk'
            value = self.model.objects.get(**{key: value})
        except (ValueError, self.queryset.model.DoesNotExist):
            raise ValidationError(self.error_messages['invalid_choice'], code='invalid_choice')
        return value

    def validate(self, value):
        """
        Validates that the input is in self.choices.
        """
        super(ChoiceField, self).validate(value)
        if value and not self.valid_value(value):
            raise ValidationError(
                self.error_messages['invalid_choice'],
                code='invalid_choice',
                params={'value': value},
            )
