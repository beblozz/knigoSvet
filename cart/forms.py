from django import forms

from .models import Order


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['name', 'phone', 'email', 'delivery', 'address', 'comment']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form__input', 'placeholder': 'Иван Иванов'}),
            'phone': forms.TextInput(attrs={'class': 'form__input', 'placeholder': '+7 (900) 000-00-00'}),
            'email': forms.EmailInput(attrs={'class': 'form__input', 'placeholder': 'mail@example.ru'}),
            'delivery': forms.Select(attrs={'class': 'form__input'}),
            'address': forms.TextInput(attrs={'class': 'form__input', 'placeholder': 'Город, улица, дом, квартира'}),
            'comment': forms.Textarea(attrs={'class': 'form__input form__input_area', 'rows': 3, 'placeholder': 'Пожелания к заказу'}),
        }

    def clean(self):
        data = super().clean()
        if data.get('delivery') != 'pickup' and not data.get('address'):
            self.add_error('address', 'Укажите адрес доставки')
        return data
