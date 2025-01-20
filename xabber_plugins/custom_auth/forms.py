from django import forms
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError


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
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password']
        )
        if self.user is None:
            self.add_error(
                'password', 'Wrong email or password.'
            )


class RegisterForm(forms.Form):
    username = forms.CharField(max_length=150, required=True, label="Username")
    email = forms.EmailField(
        label='Электронная почта',
        required=True
    )
    password = forms.CharField(
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                'autocomplete': 'new-password',
                'placeholder': 'Password'
            }
        ),
        label="Password",
        required=True,
    )
    confirm_password = forms.CharField(
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                'autocomplete': 'new-password',
                'placeholder': 'Confirm Password'
            }
        ),
        label="Confirm Password",
        required=True,
    )

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error('password', "Password do not match.")

        return cleaned_data