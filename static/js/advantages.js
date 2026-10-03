const tabs = document.querySelectorAll('.advantages__tab');
const advTitle = document.getElementById('adv-title');
const advText = document.getElementById('adv-text');
const advNumber = document.getElementById('adv-number');
const advCaption = document.getElementById('adv-caption');
let current = 0;

function showTab(index) {
    if (index < 0) {
        index = tabs.length - 1;
    }
    if (index >= tabs.length) {
        index = 0;
    }
    current = index;

    tabs.forEach(function (tab, i) {
        tab.classList.toggle('advantages__tab_active', i === index);
    });

    const tab = tabs[index];
    advTitle.textContent = tab.dataset.title;
    advText.textContent = tab.dataset.text;
    advNumber.textContent = tab.dataset.number;
    advCaption.textContent = tab.dataset.caption;
}

tabs.forEach(function (tab, i) {
    tab.addEventListener('click', function () {
        showTab(i);
    });
});

document.getElementById('adv-prev').addEventListener('click', function () {
    showTab(current - 1);
});

document.getElementById('adv-next').addEventListener('click', function () {
    showTab(current + 1);
});
