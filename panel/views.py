from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.db.models import Sum, Count, Q
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST

from cart.models import Order, OrderItem
from catalog.models import Book, Genre, Author, Review, CallRequest
from catalog.utils import make_slug
from .forms import BookForm, AuthorForm, GenreForm


def is_staff(user):
    return user.is_staff


@user_passes_test(is_staff)
def dashboard(request):
    orders = Order.objects.exclude(status='cancel')
    revenue = orders.aggregate(Sum('total'))['total__sum'] or 0
    orders_count = orders.count()
    if orders_count > 0:
        average = revenue / orders_count
    else:
        average = 0
    sold = OrderItem.objects.exclude(order__status='cancel').aggregate(Sum('quantity'))['quantity__sum'] or 0

    today = timezone.localdate()
    days = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        day_orders = orders.filter(created__date=day)
        days.append({
            'label': day.strftime('%d.%m'),
            'total': float(day_orders.aggregate(Sum('total'))['total__sum'] or 0),
            'count': day_orders.count(),
        })

    top_books = Book.objects.annotate(
        sold=Sum('order_items__quantity', filter=~Q(order_items__order__status='cancel'))
    ).filter(sold__gt=0).order_by('-sold')[:5]

    genres = Genre.objects.annotate(count=Count('books')).order_by('-count')

    statuses = []
    for key, name in Order.STATUS_CHOICES:
        statuses.append({'key': key, 'name': name, 'count': Order.objects.filter(status=key).count()})

    context = {
        'revenue': revenue,
        'orders_count': orders_count,
        'average': average,
        'sold': sold,
        'books_count': Book.objects.count(),
        'stock_count': Book.objects.aggregate(Sum('stock'))['stock__sum'] or 0,
        'users_count': User.objects.count(),
        'reviews_count': Review.objects.count(),
        'days': days,
        'top_books': top_books,
        'genres': genres,
        'statuses': statuses,
        'low_stock': Book.objects.filter(stock__lte=3).order_by('stock')[:6],
        'last_orders': Order.objects.all()[:5],
        'calls_count': CallRequest.objects.filter(is_done=False).count(),
        'active': 'dashboard',
    }
    return render(request, 'panel/dashboard.html', context)


@user_passes_test(is_staff)
def books(request):
    books = Book.objects.all()
    search = request.GET.get('q', '').strip()
    if search:
        books = books.filter(
            Q(title__contains=search) | Q(title__contains=search.capitalize()) |
            Q(author__name__contains=search) | Q(author__name__contains=search.capitalize())
        )
    return render(request, 'panel/books.html', {'books': books, 'search': search, 'active': 'books'})


@user_passes_test(is_staff)
def book_add(request):
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save(commit=False)
            slug = make_slug(book.title)
            number = 2
            while Book.objects.filter(slug=slug).exists():
                slug = make_slug(book.title) + '-' + str(number)
                number += 1
            book.slug = slug
            book.save()
            messages.success(request, 'Книга «' + book.title + '» добавлена')
            return redirect('panel_books')
    else:
        form = BookForm()
    return render(request, 'panel/book_form.html', {'form': form, 'title': 'Новая книга', 'active': 'books'})


@user_passes_test(is_staff)
def book_edit(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            form.save()
            messages.success(request, 'Изменения сохранены')
            return redirect('panel_books')
    else:
        form = BookForm(instance=book)
    return render(request, 'panel/book_form.html', {'form': form, 'title': 'Редактирование книги', 'book': book, 'active': 'books'})


@user_passes_test(is_staff)
@require_POST
def book_delete(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    title = book.title
    book.delete()
    messages.success(request, 'Книга «' + title + '» удалена')
    return redirect('panel_books')


@user_passes_test(is_staff)
def orders(request):
    orders = Order.objects.all()
    status = request.GET.get('status', '')
    if status:
        orders = orders.filter(status=status)
    context = {'orders': orders, 'status': status, 'statuses': Order.STATUS_CHOICES, 'active': 'orders'}
    return render(request, 'panel/orders.html', context)


@user_passes_test(is_staff)
@require_POST
def order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    status = request.POST.get('status')
    for key, name in Order.STATUS_CHOICES:
        if key == status:
            order.status = status
            order.save()
            messages.success(request, 'Статус заказа №' + str(order.id) + ' изменён')
    return redirect('panel_orders')


@user_passes_test(is_staff)
def extra(request):
    author_form = AuthorForm()
    genre_form = GenreForm()
    if request.method == 'POST':
        if 'author' in request.POST:
            author_form = AuthorForm(request.POST)
            if author_form.is_valid():
                author_form.save()
                messages.success(request, 'Автор добавлен')
                return redirect('panel_extra')
        if 'genre' in request.POST:
            genre_form = GenreForm(request.POST)
            if genre_form.is_valid():
                genre = genre_form.save(commit=False)
                genre.slug = make_slug(genre.name)
                genre.save()
                messages.success(request, 'Жанр добавлен')
                return redirect('panel_extra')
    context = {
        'author_form': author_form,
        'genre_form': genre_form,
        'authors': Author.objects.annotate(count=Count('books')),
        'genres': Genre.objects.annotate(count=Count('books')),
        'calls': CallRequest.objects.all()[:20],
        'active': 'extra',
    }
    return render(request, 'panel/extra.html', context)


@user_passes_test(is_staff)
@require_POST
def call_done(request, call_id):
    call = get_object_or_404(CallRequest, id=call_id)
    call.is_done = True
    call.save()
    return redirect('panel_extra')
