document.addEventListener('DOMContentLoaded', function () {
    const forms = document.querySelectorAll('form');

    forms.forEach(function (form) {
        form.addEventListener('submit', function (event) {
            const requiredFields = form.querySelectorAll('[required]');
            let hasError = false;

            requiredFields.forEach(function (field) {
                clearFieldError(field);

                if (!field.value.trim()) {
                    showFieldError(field, 'This field is required.');
                    hasError = true;
                } else if (field.type === 'email' && !isValidEmail(field.value)) {
                    showFieldError(field, 'Please enter a valid email address.');
                    hasError = true;
                } else if (field.type === 'password' && field.value.length < 6) {
                    showFieldError(field, 'Password must be at least 6 characters.');
                    hasError = true;
                }
            });

            if (hasError) {
                event.preventDefault();
            }
        });
    });

    function isValidEmail(value) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
    }

    function showFieldError(field, message) {
        field.style.borderColor = '#e74c3c';
        const errorEl = document.createElement('span');
        errorEl.className = 'field-error';
        errorEl.textContent = message;
        field.insertAdjacentElement('afterend', errorEl);
    }

    function clearFieldError(field) {
        field.style.borderColor = '';
        const next = field.nextElementSibling;
        if (next && next.classList.contains('field-error')) {
            next.remove();
        }
    }
});