import json

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from catalog.models import Book
from .forms import OrderForm
from .models import Order, OrderItem


def get_cart_items(request):
    cart = request.session.get('cart', {})
    items = []
    total = 0
    count = 0
    for book in Book.objects.filter(id__in=cart.keys()):
        quantity = cart[str(book.id)]
        price = book.price * quantity
        items.append({'book': book, 'quantity': quantity, 'price': price})
        total += price
        count += quantity
    return items, total, count


def cart_page(request):
    items, total, count = get_cart_items(request)
    return render(request, 'cart/cart.html', {'items': items, 'total': total, 'count': count})


@require_POST
def cart_add(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    cart = request.session.get('cart', {})
    key = str(book.id)
    quantity = cart.get(key, 0)
    if quantity >= book.stock:
        return JsonResponse({'ok': False, 'message': 'Больше нет на складе', 'count': sum(cart.values())})
    cart[key] = quantity + 1
    request.session['cart'] = cart
    return JsonResponse({'ok': True, 'message': 'Книга добавлена в корзину', 'count': sum(cart.values())})


@require_POST
def cart_update(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    cart = request.session.get('cart', {})
    key = str(book.id)
    data = json.loads(request.body)
    quantity = int(data.get('quantity', 1))
    if quantity < 1:
        quantity = 1
    if quantity > book.stock:
        quantity = book.stock
    cart[key] = quantity
    request.session['cart'] = cart
    items, total, count = get_cart_items(request)
    return JsonResponse({
        'quantity': quantity,
        'price': float(book.price * quantity),
        'total': float(total),
        'count': count,
    })


@require_POST
def cart_remove(request, book_id):
    cart = request.session.get('cart', {})
    key = str(book_id)
    if key in cart:
        del cart[key]
    request.session['cart'] = cart
    items, total, count = get_cart_items(request)
    return JsonResponse({'total': float(total), 'count': count})


def checkout(request):
    items, total, count = get_cart_items(request)
    if count == 0:
        return redirect('cart')

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            if request.user.is_authenticated:
                order.user = request.user
            order.total = total
            order.save()
            for item in items:
                book = item['book']
                OrderItem.objects.create(
                    order=order,
                    book=book,
                    title=book.title,
                    price=book.price,
                    quantity=item['quantity'],
                )
                book.stock = max(book.stock - item['quantity'], 0)
                book.save()
            request.session['cart'] = {}
            request.session['last_order'] = order.id
            return redirect('order_done')
    else:
        initial = {}
        if request.user.is_authenticated:
            initial['name'] = request.user.first_name
            initial['email'] = request.user.email
        form = OrderForm(initial=initial)

    return render(request, 'cart/checkout.html', {'form': form, 'items': items, 'total': total, 'count': count})


def order_done(request):
    order_id = request.session.get('last_order')
    if not order_id:
        return redirect('home')
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'cart/done.html', {'order': order})
