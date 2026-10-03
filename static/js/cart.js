const cartCount = document.getElementById('cart-count');

function updateCartCount(count) {
    cartCount.textContent = count;
    if (count > 0) {
        cartCount.classList.remove('header__count_hidden');
    } else {
        cartCount.classList.add('header__count_hidden');
    }
}

function sendPost(url, data) {
    return fetch(url, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
    }).then(function (response) {
        return response.json();
    });
}

document.querySelectorAll('.js-cart-add').forEach(function (button) {
    button.addEventListener('click', function () {
        sendPost(button.dataset.url, {}).then(function (data) {
            updateCartCount(data.count);
            showToast(data.message, !data.ok);
        });
    });
});

function updateCartPage(data) {
    updateCartCount(data.count);
    document.getElementById('cart-total').textContent = formatPrice(data.total);
    document.getElementById('cart-items').textContent = data.count;
    if (data.count === 0) {
        document.getElementById('cart-layout').classList.add('cart__layout_hidden');
        document.getElementById('cart-empty').classList.remove('empty_hidden');
    }
}

document.querySelectorAll('.js-cart-item').forEach(function (item) {
    const input = item.querySelector('.js-cart-quantity');
    const price = item.querySelector('.js-cart-price');
    const remove = item.querySelector('.js-cart-remove');

    function changeQuantity(quantity) {
        sendPost(input.dataset.url, {quantity: quantity}).then(function (data) {
            input.value = data.quantity;
            price.textContent = formatPrice(data.price);
            updateCartPage(data);
        });
    }

    item.querySelector('.js-cart-minus').addEventListener('click', function () {
        changeQuantity(Number(input.value) - 1);
    });

    item.querySelector('.js-cart-plus').addEventListener('click', function () {
        changeQuantity(Number(input.value) + 1);
    });

    input.addEventListener('change', function () {
        changeQuantity(Number(input.value));
    });

    remove.addEventListener('click', function () {
        sendPost(remove.dataset.url, {}).then(function (data) {
            item.remove();
            updateCartPage(data);
        });
    });
});
