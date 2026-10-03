const chart = document.getElementById('chart');

if (chart) {
    const bars = chart.querySelectorAll('.chart__bar');
    let max = 0;

    bars.forEach(function (bar) {
        if (Number(bar.dataset.value) > max) {
            max = Number(bar.dataset.value);
        }
    });

    setTimeout(function () {
        bars.forEach(function (bar) {
            if (max > 0) {
                bar.style.height = (Number(bar.dataset.value) / max) * 150 + 'px';
            }
        });
    }, 100);
}

const genres = document.getElementById('genres');

if (genres) {
    const fills = genres.querySelectorAll('.rows__fill');
    let max = 0;

    fills.forEach(function (fill) {
        if (Number(fill.dataset.value) > max) {
            max = Number(fill.dataset.value);
        }
    });

    setTimeout(function () {
        fills.forEach(function (fill) {
            if (max > 0) {
                fill.style.width = (Number(fill.dataset.value) / max) * 100 + '%';
            }
        });
    }, 100);
}

const modal = document.getElementById('modal');
const modalForm = document.getElementById('modal-form');
const modalText = document.getElementById('modal-text');

document.querySelectorAll('.js-delete').forEach(function (button) {
    button.addEventListener('click', function () {
        modalForm.action = button.dataset.url;
        modalText.textContent = 'Книга «' + button.dataset.title + '» будет удалена из каталога. Это действие нельзя отменить.';
        modal.classList.add('modal_open');
    });
});

document.getElementById('modal-cancel').addEventListener('click', function () {
    modal.classList.remove('modal_open');
});

modal.addEventListener('click', function (event) {
    if (event.target === modal) {
        modal.classList.remove('modal_open');
    }
});

document.querySelectorAll('.js-status').forEach(function (select) {
    select.addEventListener('change', function () {
        select.form.submit();
    });
});

const imageInput = document.getElementById('id_image');
const preview = document.getElementById('preview');

if (imageInput) {
    imageInput.addEventListener('change', function () {
        if (imageInput.files.length > 0) {
            preview.src = URL.createObjectURL(imageInput.files[0]);
            preview.classList.remove('form__preview_hidden');
        }
    });
}
