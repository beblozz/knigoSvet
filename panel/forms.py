import re
from datetime import timedelta

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils import timezone

from catalog.models import Book, Genre, Loan, Reader


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in self.fields:
            self.fields[name].widget.attrs['class'] = 'form__input'


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'genre', 'description', 'image', 'publisher', 'year', 'pages', 'isbn', 'copies']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'image': forms.FileInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in self.fields:
            if name == 'description':
                self.fields[name].widget.attrs['class'] = 'form__input form__input_area'
            else:
                self.fields[name].widget.attrs['class'] = 'form__input'
        self.fields['copies'].min_value = 1
        self.fields['copies'].widget.attrs['min'] = 1

    def clean_copies(self):
        copies = self.cleaned_data['copies']
        if copies < 1:
            raise forms.ValidationError('В фонде должен быть хотя бы один экземпляр')
        if self.instance.pk and copies < self.instance.on_hands():
            raise forms.ValidationError('Сейчас на руках ' + str(self.instance.on_hands()) + ' экз., меньше указать нельзя')
        return copies


class GenreForm(forms.ModelForm):
    class Meta:
        model = Genre
        fields = ['name']
        widgets = {'name': forms.TextInput(attrs={'class': 'form__input', 'placeholder': 'Новый жанр'})}


class ReaderForm(forms.ModelForm):
    class Meta:
        model = Reader
        fields = ['full_name', 'phone', 'email']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form__input', 'placeholder': 'Иванова Мария Петровна'}),
            'phone': forms.TextInput(attrs={'class': 'form__input', 'placeholder': '+7 900 123-45-67', 'type': 'tel'}),
            'email': forms.EmailInput(attrs={'class': 'form__input', 'placeholder': 'reader@example.ru'}),
        }
        error_messages = {
            'full_name': {'required': 'Укажите фамилию, имя и отчество'},
            'phone': {'required': 'Укажите телефон для связи'},
            'email': {'invalid': 'Проверьте адрес почты, например reader@example.ru'},
        }

    def clean_full_name(self):
        full_name = ' '.join(self.cleaned_data['full_name'].split())
        if len(full_name.split(' ')) < 2:
            raise forms.ValidationError('Нужны хотя бы фамилия и имя')
        for letter in full_name:
            if letter.isdigit():
                raise forms.ValidationError('ФИО не может содержать цифры')
        return full_name

    def clean_phone(self):
        digits = re.sub(r'\D', '', self.cleaned_data['phone'])
        if len(digits) == 10:
            digits = '7' + digits
        if len(digits) != 11 or digits[0] not in '78':
            raise forms.ValidationError('Телефон должен содержать 11 цифр, например +7 900 123-45-67')
        digits = '7' + digits[1:]
        return '+7 ' + digits[1:4] + ' ' + digits[4:7] + '-' + digits[7:9] + '-' + digits[9:11]

    def clean(self):
        data = super().clean()
        full_name = data.get('full_name')
        phone = data.get('phone')
        if full_name and phone:
            same = Reader.objects.filter(full_name=full_name, phone=phone)
            if self.instance.pk:
                same = same.exclude(pk=self.instance.pk)
            if same.exists():
                raise forms.ValidationError('Читатель с таким ФИО и телефоном уже записан: билет ' + same.first().card)
        return data


LOAN_DAYS = 14
MAX_BOOKS = 5


class BookChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, book):
        free = book.available()
        if free > 0:
            return book.title + ' — ' + book.author + ' (свободно ' + str(free) + ' из ' + str(book.copies) + ')'
        return book.title + ' — ' + book.author + ' (все экземпляры на руках)'


class ReaderChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, reader):
        return reader.card + ' · ' + reader.full_name


class LoanForm(forms.ModelForm):
    reader = ReaderChoiceField(
        queryset=Reader.objects.order_by('full_name'), label='Читатель',
        empty_label='Выберите читателя',
        error_messages={'required': 'Выберите читателя'},
    )
    book = BookChoiceField(
        queryset=Book.objects.order_by('title'), label='Книга',
        empty_label='Выберите книгу',
        error_messages={'required': 'Выберите книгу'},
    )

    class Meta:
        model = Loan
        fields = ['reader', 'book', 'issued', 'due']
        widgets = {
            'issued': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'due': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        }
        error_messages = {
            'issued': {'required': 'Укажите дату выдачи', 'invalid': 'Дата выдачи указана неверно'},
            'due': {'required': 'Укажите, до какого числа вернуть книгу', 'invalid': 'Дата возврата указана неверно'},
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        today = timezone.localdate()
        if not self.is_bound:
            self.initial.setdefault('issued', today)
            self.initial.setdefault('due', today + timedelta(days=LOAN_DAYS))
        for name in self.fields:
            self.fields[name].widget.attrs['class'] = 'form__input'

    def clean_issued(self):
        issued = self.cleaned_data['issued']
        if issued > timezone.localdate():
            raise forms.ValidationError('Дата выдачи не может быть в будущем')
        return issued

    def clean(self):
        data = super().clean()
        book = data.get('book')
        reader = data.get('reader')
        issued = data.get('issued')
        due = data.get('due')

        if issued and due:
            if due <= issued:
                self.add_error('due', 'Дата возврата должна быть позже даты выдачи')
            elif (due - issued).days > 60:
                self.add_error('due', 'Срок пользования не может быть больше 60 дней')

        if book and not book.is_available():
            self.add_error('book', 'Все экземпляры «' + book.title + '» сейчас на руках, выдать книгу нельзя')

        if reader:
            if reader.overdue() > 0:
                self.add_error('reader', 'У читателя есть просроченные книги (' + str(reader.overdue()) + '). Сначала примите их')
            elif reader.on_hands() >= MAX_BOOKS:
                self.add_error('reader', 'У читателя уже ' + str(MAX_BOOKS) + ' книг на руках, больше выдать нельзя')
            elif book and reader.loans.filter(book=book, returned__isnull=True).exists():
                self.add_error('book', 'Этот читатель уже взял «' + book.title + '» и ещё не вернул')
        return data
