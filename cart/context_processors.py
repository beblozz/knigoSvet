def cart_info(request):
    cart = request.session.get('cart', {})
    count = 0
    for quantity in cart.values():
        count += quantity
    return {'cart_count': count}
