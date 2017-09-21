from django import forms
from django.core.exceptions import ValidationError
from django.utils import six
from django.utils.encoding import force_text
from django.utils.translation import string_concat, gettext_lazy as _

from .widgets import DateRangeWidget


def to_python(self, value):
    # Try to coerce the value to unicode.
    unicode_value = force_text(value, strings_only=True)
    if isinstance(unicode_value, six.text_type):
        value = unicode_value.strip()
    else:
        raise ValidationError(
            _("Date range value given was not able to be converted to unicode.")
        )

    if self.widget.separator in value:
        str_dates = value.split(self.widget.separator, 2)

        try:
            beginning = self.to_python(str_dates[0])
        except ValidationError as e:
            raise ValidationError(string_concat('Error in period beginning: ', e.message), e.code)

        try:
            end = self.to_python(str_dates[1])
        except ValidationError as e:
            raise ValidationError(string_concat('Error in period end: ', e.message), e.code)

        return beginning, end
    else:
        raise ValidationError(
            _("Invalid date range format."),
            code='invalid'
        )


class DateRangeField(forms.DateField):
    widget = DateRangeWidget

    def to_python(self, value):
        return to_python(self, value)


class DateTimeRangeField(forms.DateTimeField):
    widget = DateRangeWidget

    def to_python(self, value):
        return to_python(self, value)
