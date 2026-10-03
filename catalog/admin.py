from django.contrib import admin

from .models import Genre, Author, Book, Review, Favorite, CallRequest


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ['name']}


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'genre', 'price', 'stock', 'is_new', 'is_bestseller']
    list_filter = ['genre', 'is_new', 'is_bestseller']
    search_fields = ['title', 'author__name']
    prepopulated_fields = {'slug': ['title']}


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['book', 'user', 'rating', 'created']


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ['user', 'book']


@admin.register(CallRequest)
class CallRequestAdmin(admin.ModelAdmin):
    list_display = ['phone', 'created', 'is_done']
