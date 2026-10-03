from django import forms

from .models import Review


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'text']
        widgets = {
            'rating': forms.Select(
                choices=[(5, '5 — отлично'), (4, '4 — хорошо'), (3, '3 — нормально'), (2, '2 — плохо'), (1, '1 — ужасно')],
                attrs={'class': 'form__input'},
            ),
            'text': forms.Textarea(attrs={'class': 'form__input form__input_area', 'rows': 4, 'placeholder': 'Что вы думаете о книге?'}),
        }
