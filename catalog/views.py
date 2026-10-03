from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from .forms import ReviewForm
from .models import Book, Genre, Author, Review, Favorite, CallRequest


def home(request):
    genres = Genre.objects.all()
    new_books = Book.objects.filter(is_new=True)[:4]
    bestsellers = Book.objects.filter(is_bestseller=True)[:9]
    context = {
        'genres': genres,
        'new_books': new_books,
        'bestsellers': bestsellers,
        'books_count': Book.objects.count(),
    }
    return render(request, 'catalog/home.html', context)


def catalog(request):
    books = Book.objects.all()
    genres = Genre.objects.all()
    authors = Author.objects.all()

    search = request.GET.get('q', '').strip()
    genre_slug = request.GET.get('genre', '')
    author_id = request.GET.get('author', '')
    price_min = request.GET.get('price_min', '')
    price_max = request.GET.get('price_max', '')
    in_stock = request.GET.get('in_stock', '')
    only_new = request.GET.get('new', '')
    sort = request.GET.get('sort', 'new')

    if search:
        words = [search, search.lower(), search.capitalize(), search.title()]
        query = Q()
        for word in words:
            query = query | Q(title__contains=word) | Q(author__name__contains=word)
        books = books.filter(query)
    if genre_slug:
        books = books.filter(genre__slug=genre_slug)
    if author_id.isdigit():
        books = books.filter(author_id=author_id)
    if price_min.isdigit():
        books = books.filter(price__gte=price_min)
    if price_max.isdigit():
        books = books.filter(price__lte=price_max)
    if in_stock:
        books = books.filter(stock__gt=0)
    if only_new:
        books = books.filter(is_new=True)

    if sort == 'cheap':
        books = books.order_by('price')
    elif sort == 'expensive':
        books = books.order_by('-price')
    elif sort == 'title':
        books = books.order_by('title')
    else:
        books = books.order_by('-created')

    paginator = Paginator(books, 9)
    page = paginator.get_page(request.GET.get('page'))

    params = request.GET.copy()
    if 'page' in params:
        params.pop('page')

    favorite_ids = []
    if request.user.is_authenticated:
        favorite_ids = list(Favorite.objects.filter(user=request.user).values_list('book_id', flat=True))

    context = {
        'page': page,
        'genres': genres,
        'authors': authors,
        'search': search,
        'genre_slug': genre_slug,
        'author_id': author_id,
        'price_min': price_min,
        'price_max': price_max,
        'in_stock': in_stock,
        'only_new': only_new,
        'sort': sort,
        'params': params.urlencode(),
        'total': paginator.count,
        'favorite_ids': favorite_ids,
    }
    return render(request, 'catalog/catalog.html', context)


def book(request, slug):
    book = get_object_or_404(Book, slug=slug)
    reviews = book.reviews.all()
    similar = Book.objects.filter(genre=book.genre).exclude(id=book.id)[:4]
    is_favorite = False
    favorite_ids = []
    if request.user.is_authenticated:
        favorite_ids = list(Favorite.objects.filter(user=request.user).values_list('book_id', flat=True))
        is_favorite = book.id in favorite_ids

    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('login')
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.book = book
            review.user = request.user
            review.save()
            messages.success(request, 'Спасибо за отзыв!')
            return redirect(book.get_absolute_url())
    else:
        form = ReviewForm()

    context = {
        'book': book,
        'reviews': reviews,
        'similar': similar,
        'form': form,
        'is_favorite': is_favorite,
        'favorite_ids': favorite_ids,
    }
    return render(request, 'catalog/book.html', context)


@login_required
@require_POST
def favorite_toggle(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    favorite = Favorite.objects.filter(user=request.user, book=book)
    if favorite.exists():
        favorite.delete()
        active = False
    else:
        Favorite.objects.create(user=request.user, book=book)
        active = True
    return JsonResponse({'active': active})


@login_required
@require_POST
def review_delete(request, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    url = review.book.get_absolute_url()
    review.delete()
    messages.success(request, 'Отзыв удалён')
    return redirect(url)


@require_POST
def call_request(request):
    phone = request.POST.get('phone', '').strip()
    digits = ''
    for symbol in phone:
        if symbol.isdigit():
            digits += symbol
    if len(digits) < 10:
        return JsonResponse({'ok': False, 'message': 'Введите номер телефона полностью'})
    CallRequest.objects.create(phone=phone)
    return JsonResponse({'ok': True, 'message': 'Спасибо! Мы перезвоним вам в ближайшее время'})
