// Main JavaScript file for general functionality across the site

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips if Bootstrap is available
    if (typeof bootstrap !== 'undefined') {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
    
    // Add fadeout functionality for alerts
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

// Helper function to format numbers with commas for thousands
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

// Helper function to generate random colors with good contrast
function generateRandomColors(count) {
    const colors = [];
    const hueStep = 360 / count;
    
    for (let i = 0; i < count; i++) {
        const hue = i * hueStep;
        colors.push(`hsl(${hue}, 70%, 60%)`);
    }
    
    return colors;
}

// Helper function to generate monochromatic color scheme for black & white theme
function generateMonochromeColors(count) {
    const colors = [];
    
    // Define our gradient from dark to light
    const baseGrays = [
        'rgba(40, 40, 40, 0.9)',    // Dark Gray
        'rgba(70, 70, 70, 0.9)',    // Gray
        'rgba(100, 100, 100, 0.9)',  // Medium Gray
        'rgba(130, 130, 130, 0.9)',  // Light Gray
        'rgba(160, 160, 160, 0.9)',  // Lighter Gray
        'rgba(200, 200, 200, 0.9)'   // Almost White
    ];
    
    // If we have fewer than baseGrays.length, just use the first 'count' colors
    if (count <= baseGrays.length) {
        return baseGrays.slice(0, count);
    }
    
    // If we need more colors, we'll interpolate between the base grays
    const step = (baseGrays.length - 1) / (count - 1);
    
    for (let i = 0; i < count; i++) {
        const index = Math.min(i * step, baseGrays.length - 1);
        const lowerIndex = Math.floor(index);
        const upperIndex = Math.ceil(index);
        
        if (lowerIndex === upperIndex) {
            colors.push(baseGrays[lowerIndex]);
        } else {
            // Create intermediate shades
            const lowerColor = baseGrays[lowerIndex];
            colors.push(lowerColor);
        }
    }
    
    return colors;
}

// Show an error message
function showError(message, elementId = 'errorMessage') {
    const errorElement = document.getElementById(elementId);
    if (errorElement) {
        errorElement.textContent = message;
        errorElement.classList.remove('d-none');
        
        // Scroll to the error message
        errorElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
        
        // Hide after 5 seconds
        setTimeout(() => {
            errorElement.classList.add('d-none');
        }, 5000);
    } else {
        console.error(message);
    }
}
