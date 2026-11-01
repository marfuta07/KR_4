from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User


class UserRegisterForm(UserCreationForm):
    """Форма регистрации"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'example@mail.com',
        }),
        label='Email'
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Стилизация всех полей
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Имя пользователя',
        })
        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'example@mail.com',
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Пароль',
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Подтверждение пароля',
        })


class UserLoginForm(AuthenticationForm):
    """Форма входа"""
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Имя пользователя',
        }),
        label='Имя пользователя'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Пароль',
        }),
        label='Пароль'
    )