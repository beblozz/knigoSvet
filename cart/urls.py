from django.urls import path

from . import views

urlpatterns = [
    path('', views.cart_page, name='cart'),
    path('add/<int:book_id>/', views.cart_add, name='cart_add'),
    path('update/<int:book_id>/', views.cart_update, name='cart_update'),
    path('remove/<int:book_id>/', views.cart_remove, name='cart_remove'),
    path('checkout/', views.checkout, name='checkout'),
    path('done/', views.order_done, name='order_done'),
]
