from django import forms

from xabber_plugins.plugins.models import Plugin


class PluginForm(forms.ModelForm):
    class Meta:
        model = Plugin
        fields = '__all__'