from django import forms

from catalog.models import Book, Author, Genre


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = [
            'title', 'author', 'genre', 'description', 'image', 'price', 'old_price',
            'stock', 'publisher', 'year', 'pages', 'isbn', 'cover', 'age', 'is_new', 'is_bestseller',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'image': forms.FileInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in self.fields:
            if name in ['is_new', 'is_bestseller']:
                self.fields[name].widget.attrs['class'] = 'form__checkbox'
            elif name == 'description':
                self.fields[name].widget.attrs['class'] = 'form__input form__input_area'
            else:
                self.fields[name].widget.attrs['class'] = 'form__input'


class AuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = ['name']
        widgets = {'name': forms.TextInput(attrs={'class': 'form__input', 'placeholder': 'Новый автор'})}


class GenreForm(forms.ModelForm):
    class Meta:
        model = Genre
        fields = ['name']
        widgets = {'name': forms.TextInput(attrs={'class': 'form__input', 'placeholder': 'Новый жанр'})}
