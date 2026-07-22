from django.contrib.auth.forms import AuthenticationForm, UsernameField
from django.forms import CharField, PasswordInput, TextInput


class LoginForm(AuthenticationForm):
    username = UsernameField(
        label_suffix='',
        widget=TextInput(
            attrs={
                'autofocus': True,
                'class': 'form-control',
                'placeholder': 'Username',
            }
        ),
    )

    password = CharField(
        label='Password',
        label_suffix='',
        strip=False,
        widget=PasswordInput(
            attrs={
                'autocomplete': 'current-password',
                'class': 'form-control',
                'placeholder': 'Password',
            }
        ),
    )
