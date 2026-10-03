const filterForm = document.getElementById('filter-form');
const filter = document.getElementById('filter');

document.getElementById('sort').addEventListener('change', function () {
    filterForm.submit();
});

filter.querySelectorAll('.filter__radio').forEach(function (input) {
    input.addEventListener('change', function () {
        filterForm.submit();
    });
});

document.getElementById('filter-button').addEventListener('click', function () {
    filter.classList.toggle('filter_open');
});
