// Main JavaScript file for general functionality across the site

document.addEventListener('DOMContentLoaded', function() {
    if (typeof bootstrap !== 'undefined') {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function(tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        setTimeout(() => {
            if (alert) {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }
        }, 5000);
    });
});

function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

function generateMonochromeColors(count) {
    const baseGrays = [
        'rgba(40, 40, 40, 0.9)',
        'rgba(70, 70, 70, 0.9)',
        'rgba(100, 100, 100, 0.9)',
        'rgba(130, 130, 130, 0.9)',
        'rgba(160, 160, 160, 0.9)',
        'rgba(200, 200, 200, 0.9)'
    ];

    if (count <= baseGrays.length) {
        return baseGrays.slice(0, count);
    }

    const colors = [];
    const step = (baseGrays.length - 1) / (count - 1);

    for (let i = 0; i < count; i++) {
        const index = Math.min(i * step, baseGrays.length - 1);
        colors.push(baseGrays[Math.floor(index)]);
    }

    return colors;
}

function showError(message, elementId = 'errorMessage') {
    const errorElement = document.getElementById(elementId);
    if (errorElement) {
        errorElement.textContent = message;
        errorElement.classList.remove('d-none');
        errorElement.scrollIntoView({ behavior: 'smooth', block: 'center' });

        setTimeout(() => {
            errorElement.classList.add('d-none');
        }, 5000);
    } else {
        console.error(message);
    }
}
