from django.core.paginator import Paginator
from django.db.models import Count, Q, Sum
from django.shortcuts import render, get_object_or_404

from .models import Book, Genre, Loan, Reader


def search_books(books, search):
    # SQLite не умеет искать без учёта регистра для русских букв,
    # поэтому проверяем несколько вариантов написания
    words = [search, search.lower(), search.capitalize(), search.title()]
    query = Q()
    for word in words:
        query = query | Q(title__contains=word) | Q(author__contains=word)
    return books.filter(query)


def only_available(books):
    result = []
    for book in books:
        if book.is_available():
            result.append(book.id)
    return books.filter(id__in=result)


def home(request):
    copies = Book.objects.aggregate(Sum('copies'))['copies__sum'] or 0
    on_hands = Loan.objects.filter(returned__isnull=True).count()
    context = {
        'genres': Genre.objects.annotate(count=Count('books')),
        'new_books': Book.objects.all()[:8],
        'books_count': Book.objects.count(),
        'free_count': copies - on_hands,
        'readers_count': Reader.objects.count(),
    }
    return render(request, 'catalog/home.html', context)


def catalog(request):
    books = Book.objects.all()

    search = request.GET.get('q', '').strip()
    genre_slug = request.GET.get('genre', '')
    free = request.GET.get('free', '')
    sort = request.GET.get('sort', 'new')

    if search:
        books = search_books(books, search)
    if genre_slug:
        books = books.filter(genre__slug=genre_slug)
    if free:
        books = only_available(books)

    if sort == 'title':
        books = books.order_by('title')
    elif sort == 'author':
        books = books.order_by('author', 'title')
    elif sort == 'year':
        books = books.order_by('-year')
    else:
        books = books.order_by('-created')

    paginator = Paginator(books, 9)
    page = paginator.get_page(request.GET.get('page'))

    params = request.GET.copy()
    if 'page' in params:
        params.pop('page')

    context = {
        'page': page,
        'genres': Genre.objects.annotate(count=Count('books')),
        'search': search,
        'genre_slug': genre_slug,
        'free': free,
        'sort': sort,
        'params': params.urlencode(),
        'total': paginator.count,
    }
    return render(request, 'catalog/catalog.html', context)


def book(request, slug):
    book = get_object_or_404(Book, slug=slug)
    similar = Book.objects.filter(genre=book.genre).exclude(id=book.id)[:4]
    nearest = book.loans.filter(returned__isnull=True).order_by('due').first()
    context = {
        'book': book,
        'similar': similar,
        'nearest': nearest,
    }
    return render(request, 'catalog/book.html', context)
