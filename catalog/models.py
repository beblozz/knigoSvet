from django.db import models
from django.urls import reverse
from django.utils import timezone


class Genre(models.Model):
    name = models.CharField('Название', max_length=100)
    slug = models.SlugField('Ссылка', unique=True)
    description = models.TextField('Описание', blank=True)

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'
        ordering = ['name']

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField('Название', max_length=200)
    slug = models.SlugField('Ссылка', unique=True, max_length=200)
    author = models.CharField('Автор', max_length=150)
    genre = models.ForeignKey(Genre, on_delete=models.PROTECT, related_name='books', verbose_name='Жанр')
    description = models.TextField('Описание', blank=True)
    image = models.ImageField('Обложка', upload_to='books/', blank=True)
    publisher = models.CharField('Издательство', max_length=150, blank=True)
    year = models.PositiveIntegerField('Год издания', default=2024)
    pages = models.PositiveIntegerField('Страниц', default=0)
    isbn = models.CharField('ISBN', max_length=20, blank=True)
    copies = models.PositiveIntegerField('Экземпляров в фонде', default=1)
    created = models.DateTimeField('Добавлена', auto_now_add=True)

    class Meta:
        verbose_name = 'Книга'
        verbose_name_plural = 'Книги'
        ordering = ['-created']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('book', args=[self.slug])

    def on_hands(self):
        return self.loans.filter(returned__isnull=True).count()

    def available(self):
        count = self.copies - self.on_hands()
        if count < 0:
            return 0
        return count

    def is_available(self):
        return self.available() > 0


class Reader(models.Model):
    full_name = models.CharField('ФИО', max_length=150)
    card = models.CharField('Номер читательского билета', max_length=20, unique=True)
    phone = models.CharField('Телефон', max_length=20)
    email = models.EmailField('Электронная почта', blank=True)
    created = models.DateTimeField('Записан', auto_now_add=True)

    class Meta:
        verbose_name = 'Читатель'
        verbose_name_plural = 'Читатели'
        ordering = ['full_name']

    def __str__(self):
        return self.full_name + ' (' + self.card + ')'

    def on_hands(self):
        return self.loans.filter(returned__isnull=True).count()

    def overdue(self):
        return self.loans.filter(returned__isnull=True, due__lt=timezone.localdate()).count()


class Loan(models.Model):
    book = models.ForeignKey(Book, on_delete=models.PROTECT, related_name='loans', verbose_name='Книга')
    reader = models.ForeignKey(Reader, on_delete=models.PROTECT, related_name='loans', verbose_name='Читатель')
    issued = models.DateField('Дата выдачи', default=timezone.localdate)
    due = models.DateField('Вернуть до')
    returned = models.DateField('Дата возврата', null=True, blank=True)

    class Meta:
        verbose_name = 'Выдача'
        verbose_name_plural = 'Журнал выдач'
        ordering = ['due']

    def __str__(self):
        return self.book.title + ' — ' + self.reader.full_name

    def is_overdue(self):
        return self.returned is None and self.due < timezone.localdate()

    def days_overdue(self):
        if not self.is_overdue():
            return 0
        return (timezone.localdate() - self.due).days
