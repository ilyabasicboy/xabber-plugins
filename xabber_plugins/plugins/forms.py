from django import forms

from xabber_plugins.plugins.models import Plugin, PluginDescription
from xabber_plugins.utils import get_language_codes


class PluginForm(forms.ModelForm):
    class Meta:
        model = Plugin
        fields = '__all__'


class PluginDescriptionForm(forms.ModelForm):

    class Meta:
        model = PluginDescription
        fields = '__all__'

    language = forms.ChoiceField(
        choices=get_language_codes(),
    )