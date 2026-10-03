from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse


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


class Author(models.Model):
    name = models.CharField('Имя', max_length=150)
    about = models.TextField('Об авторе', blank=True)

    class Meta:
        verbose_name = 'Автор'
        verbose_name_plural = 'Авторы'
        ordering = ['name']

    def __str__(self):
        return self.name


class Book(models.Model):
    COVER_CHOICES = [
        ('hard', 'Твёрдый переплёт'),
        ('soft', 'Мягкая обложка'),
    ]

    title = models.CharField('Название', max_length=200)
    slug = models.SlugField('Ссылка', unique=True, max_length=200)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='books', verbose_name='Автор')
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE, related_name='books', verbose_name='Жанр')
    description = models.TextField('Описание')
    image = models.ImageField('Обложка', upload_to='books/', blank=True)
    price = models.DecimalField('Цена', max_digits=8, decimal_places=2)
    old_price = models.DecimalField('Старая цена', max_digits=8, decimal_places=2, null=True, blank=True)
    stock = models.PositiveIntegerField('На складе', default=0)
    publisher = models.CharField('Издательство', max_length=150, blank=True)
    year = models.PositiveIntegerField('Год издания', default=2024)
    pages = models.PositiveIntegerField('Страниц', default=0)
    isbn = models.CharField('ISBN', max_length=20, blank=True)
    cover = models.CharField('Переплёт', max_length=10, choices=COVER_CHOICES, default='hard')
    age = models.CharField('Возраст', max_length=5, default='16+')
    is_new = models.BooleanField('Новинка', default=False)
    is_bestseller = models.BooleanField('Бестселлер', default=False)
    created = models.DateTimeField('Добавлена', auto_now_add=True)

    class Meta:
        verbose_name = 'Книга'
        verbose_name_plural = 'Книги'
        ordering = ['-created']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('book', args=[self.slug])

    def discount(self):
        if self.old_price and self.old_price > self.price:
            return int(100 - self.price * 100 / self.old_price)
        return 0

    def rating(self):
        reviews = self.reviews.all()
        if len(reviews) == 0:
            return 0
        total = 0
        for review in reviews:
            total += review.rating
        return round(total / len(reviews), 1)


class Review(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews', verbose_name='Книга')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews', verbose_name='Пользователь')
    rating = models.PositiveIntegerField('Оценка', default=5)
    text = models.TextField('Текст')
    created = models.DateTimeField('Дата', auto_now_add=True)

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['-created']

    def __str__(self):
        return self.book.title + ' - ' + self.user.username


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites', verbose_name='Пользователь')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='favorites', verbose_name='Книга')

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        unique_together = ['user', 'book']

    def __str__(self):
        return self.user.username + ' - ' + self.book.title


class CallRequest(models.Model):
    phone = models.CharField('Телефон', max_length=30)
    created = models.DateTimeField('Дата', auto_now_add=True)
    is_done = models.BooleanField('Обработана', default=False)

    class Meta:
        verbose_name = 'Заявка на звонок'
        verbose_name_plural = 'Заявки на звонок'
        ordering = ['-created']

    def __str__(self):
        return self.phone
