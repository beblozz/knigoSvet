from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from cart.models import Order
from catalog.models import Favorite
from .forms import RegisterForm, ProfileForm


def register(request):
    if request.user.is_authenticated:
        return redirect('profile')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Добро пожаловать в КнигоСвет!')
            return redirect('profile')
    else:
        form = RegisterForm()
    return render(request, 'users/register.html', {'form': form})


@login_required
def profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Данные сохранены')
            return redirect('profile')
    else:
        form = ProfileForm(instance=request.user)

    orders = Order.objects.filter(user=request.user)
    favorites = Favorite.objects.filter(user=request.user)
    spent = 0
    for order in orders:
        if order.status != 'cancel':
            spent += order.total

    context = {
        'form': form,
        'orders': orders,
        'favorites': favorites,
        'spent': spent,
    }
    return render(request, 'users/profile.html', context)
