from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(label='Имя', widget=forms.TextInput(attrs={'class': 'form__input'}))
    email = forms.EmailField(label='Почта', widget=forms.EmailInput(attrs={'class': 'form__input'}))

    class Meta:
        model = User
        fields = ['username', 'first_name', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in ['username', 'password1', 'password2']:
            self.fields[name].widget.attrs['class'] = 'form__input'
            self.fields[name].help_text = ''


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in self.fields:
            self.fields[name].widget.attrs['class'] = 'form__input'


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form__input'}),
            'last_name': forms.TextInput(attrs={'class': 'form__input'}),
            'email': forms.EmailInput(attrs={'class': 'form__input'}),
        }
