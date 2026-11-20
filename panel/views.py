from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Count, ProtectedError, Q, Sum
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST

from catalog.models import Book, Genre, Reader, Loan
from catalog.utils import make_slug
from catalog.views import search_books
from .forms import BookForm, GenreForm, LoanForm, ReaderForm


def is_staff(user):
    return user.is_staff


def next_card():
    # номер билета: Ч-0001, Ч-0002 и так далее — следующий после самого большого
    number = 0
    for card in Reader.objects.values_list('card', flat=True):
        digits = card.replace('Ч-', '')
        if digits.isdigit() and int(digits) > number:
            number = int(digits)
    return 'Ч-' + str(number + 1).zfill(4)


@user_passes_test(is_staff)
def dashboard(request):
    today = timezone.localdate()
    active = Loan.objects.filter(returned__isnull=True)
    copies = Book.objects.aggregate(Sum('copies'))['copies__sum'] or 0
    context = {
        'books_count': Book.objects.count(),
        'copies': copies,
        'on_hands': active.count(),
        'free': copies - active.count(),
        'overdue': active.filter(due__lt=today).count(),
        'soon': active.filter(due__gte=today, due__lte=today + timedelta(days=3)).count(),
        'readers_count': Reader.objects.count(),
        'genres': Genre.objects.annotate(count=Count('books')).order_by('-count'),
        'last_readers': Reader.objects.order_by('-created')[:5],
        'overdue_loans': active.filter(due__lt=today).select_related('book', 'reader').order_by('due')[:5],
        'active': 'dashboard',
    }
    return render(request, 'panel/dashboard.html', context)


@user_passes_test(is_staff)
def books(request):
    books = Book.objects.all()
    search = request.GET.get('q', '').strip()
    if search:
        books = search_books(books, search)
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
        messages.error(request, 'Проверьте поля, отмеченные красным')
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
        messages.error(request, 'Проверьте поля, отмеченные красным')
    else:
        form = BookForm(instance=book)
    return render(request, 'panel/book_form.html', {'form': form, 'title': 'Редактирование книги', 'book': book, 'active': 'books'})


@user_passes_test(is_staff)
@require_POST
def book_delete(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    title = book.title
    try:
        book.delete()
        messages.success(request, 'Книга «' + title + '» удалена')
    except ProtectedError:
        messages.error(request, 'Книгу «' + title + '» нельзя удалить: по ней есть записи в журнале выдач')
    return redirect('panel_books')


@user_passes_test(is_staff)
def genres(request):
    form = GenreForm()
    if request.method == 'POST':
        form = GenreForm(request.POST)
        if form.is_valid():
            genre = form.save(commit=False)
            genre.slug = make_slug(genre.name)
            if Genre.objects.filter(slug=genre.slug).exists():
                messages.error(request, 'Такой жанр уже есть')
            else:
                genre.save()
                messages.success(request, 'Жанр добавлен')
                return redirect('panel_genres')
    context = {
        'form': form,
        'genres': Genre.objects.annotate(count=Count('books')),
        'active': 'genres',
    }
    return render(request, 'panel/genres.html', context)


def text_query(field, search):
    query = Q()
    for word in [search, search.lower(), search.capitalize(), search.title()]:
        query = query | Q(**{field + '__contains': word})
    return query


@user_passes_test(is_staff)
def readers(request):
    readers = Reader.objects.annotate(
        on_hands_count=Count('loans', filter=Q(loans__returned__isnull=True)),
    )
    search = request.GET.get('q', '').strip()
    if search:
        readers = readers.filter(
            text_query('full_name', search) | text_query('card', search) | text_query('phone', search)
        )
    return render(request, 'panel/readers.html', {'readers': readers, 'search': search, 'active': 'readers'})


@user_passes_test(is_staff)
def reader_add(request):
    if request.method == 'POST':
        form = ReaderForm(request.POST)
        if form.is_valid():
            reader = form.save(commit=False)
            reader.card = next_card()
            reader.save()
            messages.success(request, 'Читатель записан, билет ' + reader.card)
            return redirect('panel_readers')
        messages.error(request, 'Проверьте поля, отмеченные красным')
    else:
        form = ReaderForm()
    context = {'form': form, 'title': 'Новый читатель', 'card': next_card(), 'active': 'readers'}
    return render(request, 'panel/reader_form.html', context)


@user_passes_test(is_staff)
def reader_edit(request, reader_id):
    reader = get_object_or_404(Reader, id=reader_id)
    if request.method == 'POST':
        form = ReaderForm(request.POST, instance=reader)
        if form.is_valid():
            form.save()
            messages.success(request, 'Данные читателя сохранены')
            return redirect('panel_readers')
        messages.error(request, 'Проверьте поля, отмеченные красным')
    else:
        form = ReaderForm(instance=reader)
    reader_loans = reader.loans.select_related('book').order_by('returned', 'due')[:20]
    context = {'form': form, 'title': 'Читатель ' + reader.card, 'card': reader.card, 'reader': reader, 'reader_loans': reader_loans, 'active': 'readers'}
    return render(request, 'panel/reader_form.html', context)


@user_passes_test(is_staff)
def loans(request):
    today = timezone.localdate()
    active = Loan.objects.filter(returned__isnull=True)
    counts = {
        'active': active.count(),
        'overdue': active.filter(due__lt=today).count(),
        'soon': active.filter(due__gte=today, due__lte=today + timedelta(days=3)).count(),
        'returned': Loan.objects.filter(returned__isnull=False).count(),
    }

    show = request.GET.get('show', 'active')
    if show == 'overdue':
        loans = active.filter(due__lt=today).order_by('due')
    elif show == 'soon':
        loans = active.filter(due__gte=today, due__lte=today + timedelta(days=3)).order_by('due')
    elif show == 'returned':
        loans = Loan.objects.filter(returned__isnull=False).order_by('-returned')
    else:
        show = 'active'
        loans = active.order_by('due')

    search = request.GET.get('q', '').strip()
    if search:
        loans = loans.filter(
            text_query('book__title', search) | text_query('book__author', search)
            | text_query('reader__full_name', search) | text_query('reader__card', search)
        )

    reader = None
    reader_id = request.GET.get('reader', '')
    if reader_id.isdigit():
        reader = Reader.objects.filter(id=reader_id).first()
        if reader:
            loans = loans.filter(reader=reader)

    context = {
        'loans': loans.select_related('book', 'reader'),
        'counts': counts,
        'show': show,
        'search': search,
        'reader': reader,
        'today': today,
        'soon_date': today + timedelta(days=3),
        'active': 'loans',
    }
    return render(request, 'panel/loans.html', context)


@user_passes_test(is_staff)
def loan_add(request):
    if request.method == 'POST':
        form = LoanForm(request.POST)
        if form.is_valid():
            loan = form.save()
            messages.success(request, '«' + loan.book.title + '» выдана: ' + loan.reader.full_name + ', вернуть до ' + loan.due.strftime('%d.%m.%Y'))
            return redirect('panel_loans')
        messages.error(request, 'Выдача не оформлена: проверьте поля, отмеченные красным')
    else:
        initial = {}
        if request.GET.get('book', '').isdigit():
            initial['book'] = request.GET['book']
        if request.GET.get('reader', '').isdigit():
            initial['reader'] = request.GET['reader']
        form = LoanForm(initial=initial)
    return render(request, 'panel/loan_form.html', {'form': form, 'active': 'loans'})


@user_passes_test(is_staff)
@require_POST
def loan_return(request, loan_id):
    loan = get_object_or_404(Loan, id=loan_id)
    if loan.returned:
        messages.error(request, 'Эта книга уже принята ' + loan.returned.strftime('%d.%m.%Y'))
    else:
        loan.returned = timezone.localdate()
        loan.save()
        text = '«' + loan.book.title + '» принята от читателя ' + loan.reader.full_name
        if loan.due < loan.returned:
            text += ', просрочка ' + str((loan.returned - loan.due).days) + ' дн.'
        messages.success(request, text)
    next_url = request.POST.get('next', '')
    if next_url.startswith('/panel/'):
        return redirect(next_url)
    return redirect('panel_loans')
