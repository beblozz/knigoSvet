from django.contrib.auth.models import User
from django.db import models

from catalog.models import Book


class Order(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новый'),
        ('paid', 'Оплачен'),
        ('sent', 'Отправлен'),
        ('done', 'Получен'),
        ('cancel', 'Отменён'),
    ]
    DELIVERY_CHOICES = [
        ('pickup', 'Самовывоз из магазина'),
        ('courier', 'Курьером'),
        ('post', 'Почтой России'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders', verbose_name='Пользователь')
    name = models.CharField('Имя', max_length=100)
    phone = models.CharField('Телефон', max_length=30)
    email = models.EmailField('Почта')
    delivery = models.CharField('Доставка', max_length=10, choices=DELIVERY_CHOICES, default='pickup')
    address = models.CharField('Адрес', max_length=250, blank=True)
    comment = models.TextField('Комментарий', blank=True)
    status = models.CharField('Статус', max_length=10, choices=STATUS_CHOICES, default='new')
    total = models.DecimalField('Сумма', max_digits=10, decimal_places=2, default=0)
    created = models.DateTimeField('Дата', auto_now_add=True)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created']

    def __str__(self):
        return 'Заказ №' + str(self.id)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name='Заказ')
    book = models.ForeignKey(Book, on_delete=models.SET_NULL, null=True, related_name='order_items', verbose_name='Книга')
    title = models.CharField('Название', max_length=200)
    price = models.DecimalField('Цена', max_digits=8, decimal_places=2)
    quantity = models.PositiveIntegerField('Количество', default=1)

    class Meta:
        verbose_name = 'Товар в заказе'
        verbose_name_plural = 'Товары в заказе'

    def __str__(self):
        return self.title

    def total(self):
        return self.price * self.quantity
