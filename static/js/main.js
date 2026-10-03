function getCookie(name) {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.startsWith(name + '=')) {
            return decodeURIComponent(cookie.slice(name.length + 1));
        }
    }
    return '';
}

function hideToast(toast) {
    setTimeout(function () {
        toast.classList.add('toasts__item_hidden');
    }, 3000);
    setTimeout(function () {
        toast.remove();
    }, 3400);
}

function showToast(text, isError) {
    const toasts = document.getElementById('toasts');
    const toast = document.createElement('div');
    toast.className = 'toasts__item';
    if (isError) {
        toast.classList.add('toasts__item_error');
    }
    toast.textContent = text;
    toasts.appendChild(toast);
    hideToast(toast);
}

function formatPrice(number) {
    return Math.round(number).toLocaleString('ru-RU') + ' ₽';
}

document.querySelectorAll('.toasts__item').forEach(function (toast) {
    hideToast(toast);
});

const burger = document.getElementById('burger');
const mobileMenu = document.getElementById('mobile-menu');

if (burger) {
    burger.addEventListener('click', function () {
        mobileMenu.classList.toggle('header__mobile_open');
    });

    mobileMenu.querySelectorAll('.header__mobile-link').forEach(function (link) {
        link.addEventListener('click', function () {
            mobileMenu.classList.remove('header__mobile_open');
        });
    });
}
