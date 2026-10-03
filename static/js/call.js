const callForm = document.getElementById('call-form');
const callResult = document.getElementById('call-result');

if (callForm) {
    callForm.addEventListener('submit', function (event) {
        event.preventDefault();

        fetch(callForm.action, {
            method: 'POST',
            body: new FormData(callForm),
        }).then(function (response) {
            return response.json();
        }).then(function (data) {
            callResult.textContent = data.message;
            callResult.classList.toggle('footer__result_error', !data.ok);
            if (data.ok) {
                callForm.reset();
            }
        });
    });
}
