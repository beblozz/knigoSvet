from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from catalog.models import Book, Reader, Loan

READERS = [
    ('Соколова Анна Дмитриевна', '+7 916 204-11-87', 'anna.sokolova@example.ru'),
    ('Левин Михаил Аркадьевич', '+7 903 555-20-14', 'levin.m@example.ru'),
    ('Ким Елена Викторовна', '+7 925 318-74-02', 'e.kim@example.ru'),
    ('Орлов Пётр Сергеевич', '+7 985 640-33-19', ''),
    ('Гусейнова Лейла Рашидовна', '+7 977 102-58-46', 'leyla.g@example.ru'),
    ('Белов Артём Игоревич', '+7 915 777-01-23', 'artem.belov@example.ru'),
    ('Захарова Ольга Николаевна', '+7 926 431-90-65', 'olga.z@example.ru'),
    ('Тимофеев Денис Олегович', '+7 999 213-44-50', ''),
]

# книга, читатель, выдана дней назад, срок в днях, вернул через N дней (None — на руках)
LOANS = [
    ('master-i-margarita', 0, 20, 14, None),
    ('1984', 1, 18, 14, None),
    ('dyuna', 2, 10, 14, None),
    ('sapiens', 3, 12, 14, None),
    ('hobbit', 4, 30, 21, 19),
    ('malenkiy-princ', 5, 3, 14, None),
    ('prestuplenie-i-nakazanie', 6, 25, 21, None),
    ('sobaka-baskerviley', 7, 40, 14, 12),
    ('evgeniy-onegin', 0, 6, 14, None),
    ('aviator', 2, 13, 14, None),
    ('anna-karenina', 1, 50, 21, 20),
    ('piknik-na-obochine', 5, 1, 14, None),
]


class Command(BaseCommand):
    help = 'Создаёт тестовых читателей и записи журнала выдач относительно сегодняшней даты'

    def handle(self, *args, **options):
        Loan.objects.all().delete()
        Reader.objects.all().delete()
        readers = []
        for number, (full_name, phone, email) in enumerate(READERS, start=1):
            reader = Reader.objects.create(
                full_name=full_name, phone=phone, email=email, card='Ч-' + str(number).zfill(4),
            )
            readers.append(reader)

        today = timezone.localdate()
        count = 0
        for slug, reader_index, ago, term, returned_after in LOANS:
            book = Book.objects.filter(slug=slug).first()
            if book is None:
                continue
            issued = today - timedelta(days=ago)
            returned = None
            if returned_after is not None:
                returned = issued + timedelta(days=returned_after)
            Loan.objects.create(
                book=book, reader=readers[reader_index], issued=issued,
                due=issued + timedelta(days=term), returned=returned,
            )
            count += 1

        self.stdout.write(self.style.SUCCESS(
            'Читателей: ' + str(len(readers)) + ', записей в журнале: ' + str(count)
        ))
