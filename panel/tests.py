from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from catalog.models import Book, Genre, Loan, Reader


class LibraryTests(TestCase):
    def setUp(self):
        self.today = timezone.localdate()
        User.objects.create_user('lib', password='pass12345', is_staff=True)
        self.client.login(username='lib', password='pass12345')
        genre = Genre.objects.create(name='Классика', slug='klassika')
        self.book = Book.objects.create(title='Мастер и Маргарита', slug='master', author='Михаил Булгаков', genre=genre, copies=1)
        self.other = Book.objects.create(title='Белая гвардия', slug='gvardiya', author='Михаил Булгаков', genre=genre, copies=2)
        self.reader = Reader.objects.create(full_name='Соколова Анна Дмитриевна', card='Ч-0001', phone='+7 916 204-11-87')
        self.second = Reader.objects.create(full_name='Левин Михаил Аркадьевич', card='Ч-0002', phone='+7 903 555-20-14')

    def issue(self, reader, book, due_days=14, issued=None):
        issued = issued or self.today
        return self.client.post('/panel/loans/add/', {
            'reader': reader.id, 'book': book.id,
            'issued': issued.isoformat(), 'due': (issued + timedelta(days=due_days)).isoformat(),
        })

    def test_issue_book(self):
        response = self.issue(self.reader, self.book)
        self.assertRedirects(response, '/panel/loans/')
        self.assertEqual(self.book.available(), 0)

    def test_busy_book_cannot_be_issued_again(self):
        self.issue(self.reader, self.book)
        response = self.issue(self.second, self.book)
        self.assertContains(response, 'сейчас на руках, выдать книгу нельзя')
        self.assertEqual(Loan.objects.count(), 1)

    def test_same_reader_same_book(self):
        self.issue(self.reader, self.other)
        response = self.issue(self.reader, self.other)
        self.assertContains(response, 'уже взял')

    def test_return_frees_copy(self):
        self.issue(self.reader, self.book)
        loan = Loan.objects.get()
        self.client.post('/panel/loans/%d/return/' % loan.id)
        loan.refresh_from_db()
        self.assertEqual(loan.returned, self.today)
        self.assertTrue(self.book.is_available())
        response = self.client.post('/panel/loans/%d/return/' % loan.id, follow=True)
        self.assertContains(response, 'уже принята')

    def test_overdue_is_highlighted_and_blocks_new_loan(self):
        Loan.objects.create(book=self.other, reader=self.reader, issued=self.today - timedelta(days=20), due=self.today - timedelta(days=6))
        response = self.client.get('/panel/loans/?show=overdue')
        self.assertContains(response, 'table__row_overdue')
        self.assertContains(response, 'Просрочено 6 дн.')
        response = self.issue(self.reader, self.book)
        self.assertContains(response, 'есть просроченные книги')

    def test_required_fields_and_dates(self):
        response = self.client.post('/panel/loans/add/', {})
        self.assertContains(response, 'Выберите читателя')
        self.assertContains(response, 'Выберите книгу')
        response = self.issue(self.reader, self.book, due_days=-1)
        self.assertContains(response, 'должна быть позже даты выдачи')
        response = self.issue(self.reader, self.book, due_days=90)
        self.assertContains(response, 'не может быть больше 60 дней')

    def test_search_without_results(self):
        response = self.client.get('/catalog/?q=несуществующая')
        self.assertContains(response, 'Ничего не нашлось')
        response = self.client.get('/panel/loans/?q=несуществующая')
        self.assertContains(response, 'записей нет')

    def test_search_by_author_lowercase(self):
        response = self.client.get('/catalog/?q=булгаков')
        self.assertContains(response, 'Мастер и Маргарита')
        self.assertContains(response, 'Белая гвардия')

    def test_book_form_and_edit(self):
        response = self.client.post('/panel/books/add/', {'title': '', 'author': '', 'year': 2024, 'pages': 10, 'copies': 0})
        self.assertContains(response, 'form__field_error')
        response = self.client.post('/panel/books/add/', {
            'title': 'Собачье сердце', 'author': 'Михаил Булгаков', 'genre': self.book.genre.id,
            'year': 2020, 'pages': 160, 'copies': 2,
        })
        self.assertRedirects(response, '/panel/books/')
        book = Book.objects.get(title='Собачье сердце')
        self.client.post('/panel/books/%d/edit/' % book.id, {
            'title': 'Собачье сердце', 'author': 'Михаил Булгаков', 'genre': self.book.genre.id,
            'year': 2021, 'pages': 160, 'copies': 3,
        })
        book.refresh_from_db()
        self.assertEqual(book.copies, 3)

    def test_copies_not_less_than_on_hands(self):
        self.issue(self.reader, self.other)
        self.issue(self.second, self.other)
        response = self.client.post('/panel/books/%d/edit/' % self.other.id, {
            'title': self.other.title, 'author': self.other.author, 'genre': self.other.genre.id,
            'year': 2020, 'pages': 100, 'copies': 1,
        })
        self.assertContains(response, 'меньше указать нельзя')

    def test_reader_form_errors(self):
        response = self.client.post('/panel/readers/add/', {'full_name': 'Иванов', 'phone': '123', 'email': 'mail@'})
        self.assertContains(response, 'Нужны хотя бы фамилия и имя')
        self.assertContains(response, 'Телефон должен содержать 11 цифр')
        response = self.client.post('/panel/readers/add/', {'full_name': 'Соколова Анна Дмитриевна', 'phone': '89162041187'})
        self.assertContains(response, 'уже записан')

    def test_panel_needs_login(self):
        self.client.logout()
        response = self.client.get('/panel/loans/')
        self.assertEqual(response.status_code, 302)
