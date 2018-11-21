from datetime import date

from django.forms import forms
from django.test import SimpleTestCase

from bootstrap_daterangepicker.fields import DateRangeField


class DateRangeTests(SimpleTestCase):
    def test_default_setup(self):
        class TestForm(forms.Form):
            dates = DateRangeField()

        form = TestForm({'dates': '2018-01-01 - 2018-01-31'})
        self.assertTrue(form.is_bound)
        self.assertTrue(form.is_valid(), msg=form.errors)
        start, end = form.cleaned_data['dates']
        self.assertEqual(start, date(2018, 1, 1))
        self.assertEqual(end, date(2018, 1, 31))

    def test_required_not_set_raises_error(self):
        class TestForm(forms.Form):
            dates = DateRangeField(required=True)

        form = TestForm({})
        self.assertFalse(form.is_valid())
        self.assertDictEqual(form.errors, {'dates': ['This field is required.']})

    def test_required_empty_raises_error(self):
        class TestForm(forms.Form):
            dates = DateRangeField(required=True)

        form = TestForm({'dates': ''})  # when the form is empty it is actually passed as an empty string
        self.assertFalse(form.is_valid())
        # FIXME: really this should be {'dates': ['This field is required.']} which only happens if to_python doesn't return a validation error
        self.assertDictEqual(form.errors, {'dates': ['Invalid date range format.']})

    def test_not_required_not_set(self):
        class TestForm(forms.Form):
            dates = DateRangeField(required=False)

        form = TestForm({})  # bind the form to an empty request
        self.assertTrue(form.is_valid(), msg=form.errors)
        start, end = form.cleaned_data['dates']
        self.assertIsNone(start)
        self.assertIsNone(end)

    def test_not_required_empty(self):
        class TestForm(forms.Form):
            dates = DateRangeField(required=False)

        form = TestForm({'dates': ''})  # when the form is empty it is actually passed as an empty string
        self.assertTrue(form.is_valid(), msg=form.errors)
        start, end = form.cleaned_data['dates']
        self.assertIsNone(start)
        self.assertIsNone(end)

    def test_not_required_set(self):
        class TestForm(forms.Form):
            dates = DateRangeField(required=False)

        form = TestForm({'dates': '2018-01-01 - 2018-01-31'})
        self.assertTrue(form.is_valid(), msg=form.errors)
        start, end = form.cleaned_data['dates']
        self.assertEqual(start, date(2018, 1, 1))
        self.assertEqual(end, date(2018, 1, 31))

    def test_with_date_instances(self):
        class TestForm(forms.Form):
            dates = DateRangeField(required=True)

        start, end = (date(2018, 8, 1), date(2018, 8, 3))
        form = TestForm({'dates': (start, end)})
        self.assertTrue(form.is_valid(), msg=form.errors)
        start, end = form.cleaned_data['dates']
        self.assertEqual(start, date(2018, 8, 1))
        self.assertEqual(end, date(2018, 8, 3))
