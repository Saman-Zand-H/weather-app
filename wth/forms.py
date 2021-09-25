from django import forms

from .models import WEATHERUNIT_CHOICES

class FindCityForm(forms.Form):
    location = forms.CharField(max_length=40, widget=forms.TextInput(attrs={
        'placeholder': 'Find your location ...'
    }), required=False)

class ContactForm(forms.Form):
    name = forms.CharField(required=False)
    message = forms.CharField(required=False, widget=forms.Textarea())

class UnitForm(forms.Form):
    unit = forms.ChoiceField(required=False, choices=WEATHERUNIT_CHOICES)

class CitiesForm(forms.Form):
    default_city = forms.CharField(required=False)

class RemoveCityForm(forms.Form):
    city = forms.CharField(required=False)