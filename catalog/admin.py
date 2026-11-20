from django.contrib import admin

from .models import Genre, Book, Reader, Loan


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ['name']}


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'genre', 'year', 'copies']
    list_filter = ['genre']
    search_fields = ['title', 'author']
    prepopulated_fields = {'slug': ['title']}


@admin.register(Reader)
class ReaderAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'card', 'phone', 'email']
    search_fields = ['full_name', 'card', 'phone']


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ['book', 'reader', 'issued', 'due', 'returned']
    list_filter = ['returned']
