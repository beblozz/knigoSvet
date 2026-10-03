const track = document.getElementById('slider-track');
const thumb = document.getElementById('slider-thumb');
const slides = track.querySelectorAll('.slider__item');

function updateSlider() {
    const center = track.scrollLeft + track.clientWidth / 2;
    let active = slides[0];
    let minDistance = Infinity;

    slides.forEach(function (slide) {
        const slideCenter = slide.offsetLeft + slide.offsetWidth / 2;
        const distance = Math.abs(center - slideCenter);
        if (distance < minDistance) {
            minDistance = distance;
            active = slide;
        }
    });

    slides.forEach(function (slide) {
        slide.classList.toggle('slider__item_active', slide === active);
    });

    const maxScroll = track.scrollWidth - track.clientWidth;
    const bar = thumb.parentElement;
    const maxLeft = bar.clientWidth - thumb.clientWidth;
    thumb.style.left = (track.scrollLeft / maxScroll) * maxLeft + 'px';
}

track.addEventListener('scroll', updateSlider);
window.addEventListener('resize', updateSlider);

const middle = slides[Math.floor(slides.length / 2)];
track.scrollLeft = middle.offsetLeft + middle.offsetWidth / 2 - track.clientWidth / 2;
updateSlider();
