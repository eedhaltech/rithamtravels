/**
 * Unified Popup System for Ritham Tours
 * This file provides a consistent popup/alert system across the entire website
 */

/**
 * Show a popup modal with custom message and type
 * @param {string} message - The message to display
 * @param {string} type - Type of popup: 'success', 'error', 'warning', 'info'
 * @param {string} title - Optional custom title
 * @param {function} callback - Optional callback function to execute after closing
 */
function showPopup(message, type = 'info', title = null, callback = null) {
    const modal = document.getElementById('unifiedPopupModal');
    if (!modal) {
        console.error('Unified popup modal not found. Falling back to alert.');
        window.originalAlert(message);
        if (callback) callback();
        return;
    }
    
    const modalHeader = document.getElementById('popupModalHeader');
    const modalTitle = document.getElementById('popupModalTitle');
    const modalIcon = document.getElementById('popupModalIcon');
    const modalBody = document.getElementById('popupModalBody');
    const modalButton = document.getElementById('popupModalButton');
    
    // Remove all type classes
    modalHeader.classList.remove('success', 'error', 'warning', 'info');
    
    // Set icon and title based on type
    let iconClass = '';
    let defaultTitle = '';
    
    switch(type.toLowerCase()) {
        case 'success':
            iconClass = 'bi-check-circle-fill';
            defaultTitle = 'Success';
            modalHeader.classList.add('success');
            modalButton.className = 'btn btn-success';
            break;
        case 'error':
        case 'danger':
            iconClass = 'bi-x-circle-fill';
            defaultTitle = 'Error';
            modalHeader.classList.add('error');
            modalButton.className = 'btn btn-danger';
            break;
        case 'warning':
            iconClass = 'bi-exclamation-triangle-fill';
            defaultTitle = 'Warning';
            modalHeader.classList.add('warning');
            modalButton.className = 'btn btn-warning';
            break;
        case 'info':
        default:
            iconClass = 'bi-info-circle-fill';
            defaultTitle = 'Information';
            modalHeader.classList.add('info');
            modalButton.className = 'btn btn-primary';
            break;
    }
    
    // Set icon
    modalIcon.className = 'bi ' + iconClass + ' me-2';
    
    // Set title
    modalTitle.textContent = title || defaultTitle;
    
    // Set message
    modalBody.innerHTML = message;
    
    // Handle callback
    if (callback && typeof callback === 'function') {
        modalButton.onclick = function() {
            const bsModal = bootstrap.Modal.getInstance(modal);
            if (bsModal) {
                bsModal.hide();
            }
            callback();
        };
        
        // Also handle when modal is closed by clicking outside or pressing ESC
        modal.addEventListener('hidden.bs.modal', function handler() {
            callback();
            modal.removeEventListener('hidden.bs.modal', handler);
        }, { once: true });
    } else {
        modalButton.onclick = null;
    }
    
    // Show modal
    const bsModal = new bootstrap.Modal(modal);
    bsModal.show();
}

/**
 * Show alert container (for inline alerts in forms)
 * @param {string} message - The message to display
 * @param {string} type - Type of alert: 'success', 'danger', 'warning', 'info'
 * @param {string} containerId - ID of the container element (default: 'alertContainer')
 */
function showAlert(message, type = 'info', containerId = 'alertContainer') {
    const alertContainer = document.getElementById(containerId);
    if (!alertContainer) {
        // Fallback to popup if container not found
        showPopup(message, type);
        return;
    }
    
    // Map type names
    const alertType = type === 'error' ? 'danger' : type;
    
    alertContainer.innerHTML = `
        <div class="alert alert-${alertType} alert-dismissible fade show" role="alert">
            <i class="bi ${getAlertIcon(alertType)} me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        const alert = alertContainer.querySelector('.alert');
        if (alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }
    }, 5000);
}

/**
 * Get Bootstrap icon class for alert type
 */
function getAlertIcon(type) {
    switch(type) {
        case 'success': return 'bi-check-circle-fill';
        case 'danger': return 'bi-x-circle-fill';
        case 'warning': return 'bi-exclamation-triangle-fill';
        case 'info': return 'bi-info-circle-fill';
        default: return 'bi-info-circle-fill';
    }
}

// Store original alert function
window.originalAlert = window.alert;

// Override native alert() to use our popup system
window.alert = function(message) {
    showPopup(message, 'info');
};

// Make functions globally available
window.showPopup = showPopup;
window.showAlert = showAlert;
