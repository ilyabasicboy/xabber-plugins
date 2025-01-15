from django import forms
from django.contrib.auth import authenticate


class CustomAuthenticationForm(forms.Form):
    """
    Base class for authenticating users. Extend this to get a form that accepts
    username/password logins.
    """
    email = forms.EmailField(
        label='email'
    )
    password = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                'autocomplete': 'current-password',
                'placeholder': 'Password'
            }
        ),
    )

    def __init__(self, *args, request=None, **kwargs):

        """ add request in arguments to provide it in authenticate func """

        self.request = request
        super(CustomAuthenticationForm, self).__init__(*args, **kwargs)

    def clean(self):
        super(CustomAuthenticationForm, self).clean()
        self.user = authenticate(
            username=self.cleaned_data['email'],
            password=self.cleaned_data['password']
        )
        if self.user is None:
            self.add_error(
                'password', 'Wrong email or password.'
            )
