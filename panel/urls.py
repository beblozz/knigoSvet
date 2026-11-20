from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from . import views
from .forms import LoginForm

urlpatterns = [
    path('', views.dashboard, name='panel'),
    path('login/', LoginView.as_view(template_name='panel/login.html', authentication_form=LoginForm), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('books/', views.books, name='panel_books'),
    path('books/add/', views.book_add, name='panel_book_add'),
    path('books/<int:book_id>/edit/', views.book_edit, name='panel_book_edit'),
    path('books/<int:book_id>/delete/', views.book_delete, name='panel_book_delete'),
    path('genres/', views.genres, name='panel_genres'),
    path('readers/', views.readers, name='panel_readers'),
    path('readers/add/', views.reader_add, name='panel_reader_add'),
    path('readers/<int:reader_id>/edit/', views.reader_edit, name='panel_reader_edit'),
    path('loans/', views.loans, name='panel_loans'),
    path('loans/add/', views.loan_add, name='panel_loan_add'),
    path('loans/<int:loan_id>/return/', views.loan_return, name='panel_loan_return'),
]
