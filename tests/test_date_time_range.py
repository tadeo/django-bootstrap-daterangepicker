from datetime import datetime

from django.forms import forms
from django.test import SimpleTestCase
from django.utils.timezone import get_current_timezone

from bootstrap_daterangepicker.fields import DateTimeRangeField

tz = get_current_timezone()


class DateTimeRangeTests(SimpleTestCase):
    def test_default_setup(self):
        class TestForm(forms.Form):
            dates = DateTimeRangeField()

        form = TestForm({'dates': '2018-01-01 - 2018-01-31'})
        self.assertTrue(form.is_bound)
        self.assertTrue(form.is_valid(), msg=form.errors)
        start, end = form.cleaned_data['dates']
        self.assertEqual(start, datetime(2018, 1, 1, tzinfo=tz))
        self.assertEqual(end, datetime(2018, 1, 31, tzinfo=tz))

    def test_required_not_set_raises_error(self):
        class TestForm(forms.Form):
            dates = DateTimeRangeField(required=True)

        form = TestForm({})
        self.assertFalse(form.is_valid())
        self.assertDictEqual(form.errors, {'dates': ['This field is required.']})

    def test_required_empty_raises_error(self):
        class TestForm(forms.Form):
            dates = DateTimeRangeField(required=True)

        form = TestForm({'dates': ''})  # when the form is empty it is actually passed as an empty string
        self.assertFalse(form.is_valid())
        # FIXME: really this should be {'dates': ['This field is required.']} which only happens if to_python doesn't return a validation error
        self.assertDictEqual(form.errors, {'dates': ['Invalid date range format.']})

    def test_not_required_not_set(self):
        class TestForm(forms.Form):
            dates = DateTimeRangeField(required=False)

        form = TestForm({})  # bind the form to an empty request
        self.assertTrue(form.is_valid(), msg=form.errors)
        start, end = form.cleaned_data['dates']
        self.assertIsNone(start)
        self.assertIsNone(end)

    def test_not_required_empty(self):
        class TestForm(forms.Form):
            dates = DateTimeRangeField(required=False)

        form = TestForm({'dates': ''})  # when the form is empty it is actually passed as an empty string
        self.assertTrue(form.is_valid(), msg=form.errors)
        start, end = form.cleaned_data['dates']
        self.assertIsNone(start)
        self.assertIsNone(end)

    def test_not_required_set(self):
        class TestForm(forms.Form):
            dates = DateTimeRangeField(required=False)

        form = TestForm({'dates': '2018-01-01 - 2018-01-31'})
        self.assertTrue(form.is_valid(), msg=form.errors)
        start, end = form.cleaned_data['dates']
        self.assertEqual(start, datetime(2018, 1, 1, tzinfo=tz))
        self.assertEqual(end, datetime(2018, 1, 31, tzinfo=tz))

    def test_with_date_instances(self):
        class TestForm(forms.Form):
            dates = DateTimeRangeField(required=True)

        form = TestForm({'dates': (datetime(2018, 8, 1, tzinfo=tz), datetime(2018, 8, 3, tzinfo=tz))})
        self.assertTrue(form.is_valid(), msg=form.errors)
        start, end = form.cleaned_data['dates']
        self.assertEqual(start, datetime(2018, 8, 1, tzinfo=tz))
        self.assertEqual(end, datetime(2018, 8, 3, tzinfo=tz))
