document.querySelectorAll('.js-favorite').forEach(function (button) {
    button.addEventListener('click', function () {
        if (document.body.dataset.auth === '0') {
            window.location.href = document.body.dataset.login;
            return;
        }

        fetch(button.dataset.url, {
            method: 'POST',
            headers: {'X-CSRFToken': getCookie('csrftoken')},
        }).then(function (response) {
            return response.json();
        }).then(function (data) {
            if (button.dataset.text) {
                button.classList.toggle('book__favorite_active', data.active);
                button.textContent = data.active ? 'В избранном' : 'В избранное';
            } else {
                button.classList.toggle('book-card__favorite_active', data.active);
            }
            showToast(data.active ? 'Добавлено в избранное' : 'Удалено из избранного');
        });
    });
});
