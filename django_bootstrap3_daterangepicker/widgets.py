import json
import re
from dateutil import relativedelta

from collections import OrderedDict

from datetime import date, datetime, timedelta
from django import forms
from django.utils import formats
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

__all__ = ['DateRangeWidget', 'add_month', 'common_dates']

format_to_js = {
    '%m': 'MM',
    '%d': 'DD',
    '%Y': 'YYYY',
    '%y': 'YY',
    '%B': 'MMMM',
    '%b': 'MMM',
    '%M': 'mm',
    '%H': 'hh',
    '%I': 'h',
    '%p': 'A',
    '%S': 'ss',
}

format_to_js_re = re.compile(r'(?<!\w)(' + '|'.join(format_to_js.keys()) + r')\b')


def add_month(start_date, months):
    return start_date + relativedelta.relativedelta(months=months)


def common_dates(start_date=date.today()):
    one_day = timedelta(days=1)
    return OrderedDict([
        ('Today',  (start_date, start_date)),
        ('Yesterday', (start_date - one_day, start_date - one_day)),
        ('This week', (start_date - timedelta(days=start_date.weekday()), start_date)),
        ('Last week', (start_date - timedelta(days=start_date.weekday() + 7),
                       start_date - timedelta(days=start_date.weekday() + 1))),
        ('Week ago', (start_date - timedelta(days=7), start_date)),
        ('This month', (start_date.replace(day=1), start_date)),
        ('Last month', (add_month(start_date.replace(day=1), -1), start_date.replace(day=1) - one_day)),
        ('3 months', (add_month(start_date, -3), start_date)),
        ('Year', (add_month(start_date, -12), start_date)),
    ])


class DateRangeWidget(forms.TextInput):
    format_key = 'DATE_INPUT_FORMATS'

    def __init__(self, picker_options=None, attrs=None, format=None, separator=' - ', clearable=False):
        super(DateRangeWidget, self).__init__(attrs)
        self.separator = separator
        self.format = format
        self.picker_options = picker_options or {}
        self.clearable = clearable

    def __format(self):
        return self.format or formats.get_format(self.format_key)[0]

    def __format_date(self, value):
        return formats.localize_input(value, self.__format())

    def _format_value(self, value):
        if isinstance(value, tuple):
            return self.__format_date(value[0]) + \
                   self.separator + \
                   self.__format_date(value[1])
        else:
            return value

    script_template = """
        <script type="text/javascript">
        $(function() {{
            $('#{id}').daterangepicker({options});
        }});
        </script>
        """

    clearable_script_template = """
        <script type="text/javascript">
        $(function() {{
        
            $('#{id}').on('apply.daterangepicker', function(ev, picker) {{
                $(this).val(picker.startDate.format('{js_format}') + '{separator}' + picker.endDate.format('{js_format}'));
            }});
            
            $('#{id}').on('cancel.daterangepicker', function(ev, picker) {{
                $(this).val('');
            }});
            
        }});
        </script>
        """

    date_options = {'startDate', 'endDate', 'minDate', 'maxDate'}

    def render(self, name, value, attrs=None):
        date_format = self.__format()
        js_format = format_to_js_re.sub(lambda m: format_to_js[m.group()], date_format)

        options = {
            'locale': {
                'format': js_format
            }
        }

        if self.clearable:
            options['autoUpdateInput'] = False
            options['locale']['cancelLabel'] = _("Clear")

        def convert_dates(v):
            if callable(v):
                v = v()

            if isinstance(v, date) or isinstance(v, datetime):
                return v.strftime(date_format)
            else:
                return str(v)

        picker_options = self.picker_options if not callable(self.picker_options) else self.picker_options()
        options.update(picker_options)
        if 'ranges' in options:
            ranges = OrderedDict(options['ranges'])
            for k, v in ranges.items():
                if callable(v):
                    ranges[k] = v(datetime.today())
            options['ranges'] = ranges

        options_js = json.dumps(options, default=convert_dates, indent="    ")

        attrs = self.build_attrs(self.attrs, attrs)
        script = self.script_template.format(id=attrs['id'], options=options_js)

        clearable_script = ""
        if self.clearable:
            clearable_script = self.clearable_script_template.format(
                id=attrs['id'],
                separator=self.separator,
                js_format=options['locale']['format'],
            )

        if 'class' not in attrs:
            attrs['class'] = 'form-control'
        return mark_safe(super(DateRangeWidget, self).render(name, value, attrs) + script + clearable_script)

    class Media:
        css = {
            'all': ('daterangepicker/daterangepicker.css',)
        }
        js = ('momentjs/moment.js', 'daterangepicker/daterangepicker.js')


class DateTimeRangeWidget(DateRangeWidget):
    format_key = 'DATETIME_INPUT_FORMATS'

    def __init__(self, *args, **kwargs):
        super(DateTimeRangeWidget, self).__init__(*args, **kwargs)

        # If picker options are not set already, add make picker a timePicker
        if not self.picker_options:
            self.picker_options = {'timePicker': True}
