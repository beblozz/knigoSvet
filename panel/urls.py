from django.urls import path

from . import views

urlpatterns = [
    path('', views.dashboard, name='panel'),
    path('books/', views.books, name='panel_books'),
    path('books/add/', views.book_add, name='panel_book_add'),
    path('books/<int:book_id>/edit/', views.book_edit, name='panel_book_edit'),
    path('books/<int:book_id>/delete/', views.book_delete, name='panel_book_delete'),
    path('orders/', views.orders, name='panel_orders'),
    path('orders/<int:order_id>/status/', views.order_status, name='panel_order_status'),
    path('extra/', views.extra, name='panel_extra'),
    path('calls/<int:call_id>/done/', views.call_done, name='panel_call_done'),
]
