from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('catalog/', views.catalog, name='catalog'),
    path('book/<slug:slug>/', views.book, name='book'),
    path('favorite/<int:book_id>/', views.favorite_toggle, name='favorite_toggle'),
    path('review/<int:review_id>/delete/', views.review_delete, name='review_delete'),
    path('call/', views.call_request, name='call_request'),
]
