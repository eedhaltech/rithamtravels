/**
 * Multicity Form Core Validation Library
 * Provides consistent validation logic for multicity forms across the application
 */

class MulticityValidator {
    constructor(options = {}) {
        this.containerId = options.containerId || 'multicityFields';
        this.enableSightseeing = options.enableSightseeing || false;
        this.maxRows = options.maxRows || 10;
        this.enableContinuityCheck = options.enableContinuityCheck || false;
        this.enableCircularRouteCheck = options.enableCircularRouteCheck || false;
        
        // Configuration
        this.config = {
            messages: {
                required: 'This field is required',
                pickupCityRequired: 'Please select a pickup city first.',
                dateRequired: 'Please select a date',
                fromCityRequired: 'Please select a from location',
                toCityRequired: 'Please select a to location',
                pastDate: 'Date cannot be in the past',
                dateSequence: 'Date cannot be before the previous row\'s date',
                routeContinuity: '"From" location must match the previous row\'s "To" location. Route must be continuous.',
                maxRowsReached: `Maximum ${this.maxRows} rows allowed`,
                completeCurrentRow: 'Please complete the current row before adding a new one',
                minRowsRequired: 'At least one row is required',
                validationSuccess: 'Route validation successful!',
                validationFailed: 'Route Validation Failed'
            },
            timing: {
                validationDelay: 1500
            }
        };
        
        this.init();
    }
    
    init() {
        console.log('Initializing MulticityValidator with options:', {
            containerId: this.containerId,
            enableSightseeing: this.enableSightseeing,
            maxRows: this.maxRows,
            enableContinuityCheck: this.enableContinuityCheck,
            enableCircularRouteCheck: this.enableCircularRouteCheck
        });
        
        this.bindCoreEvents();
        this.setupValidation();
        this.updateRemoveButtons();
    }
    
    // Core validation methods
    validatePickupCity() {
        const pickupCity = document.getElementById('multicity_pickup_city');
        if (!pickupCity) return true;
        
        if (!pickupCity.value.trim()) {
            alert(this.config.messages.pickupCityRequired);
            pickupCity.focus();
            return false;
        }
        
        return true;
    }
    
    validateDate(dateInput) {
        if (!dateInput.value) {
            this.showFieldError(dateInput, this.config.messages.dateRequired);
            return false;
        }
        
        const selectedDate = new Date(dateInput.value);
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        
        if (selectedDate < today) {
            this.showFieldError(dateInput, this.config.messages.pastDate);
            return false;
        }
        
        this.clearFieldError(dateInput);
        return true;
    }
    
    validateRequired(element, fieldName) {
        if (!element.value.trim()) {
            this.showFieldError(element, `${fieldName} is required`);
            return false;
        }
        this.clearFieldError(element);
        return true;
    }
    
    validateMulticityRow(rowElement, index) {
        const date = rowElement.querySelector('.multicity-date');
        const fromCity = rowElement.querySelector('.from-city');
        const toCity = rowElement.querySelector('.to-city');
        
        let isValid = true;
        
        // Validate date
        if (!this.validateDate(date)) {
            isValid = false;
        }
        
        // Validate cities
        if (!this.validateRequired(fromCity, 'From location')) {
            isValid = false;
        }
        
        if (!this.validateRequired(toCity, 'To location')) {
            isValid = false;
        }
        
        // Validate cities are different
        if (fromCity.value && toCity.value && fromCity.value === toCity.value) {
            this.showFieldError(toCity, 'To city cannot be same as from city');
            isValid = false;
        }
        
        return isValid;
    }
    
    validateDateSequence(rows) {
        let previousDate = null;
        let isValid = true;
        
        rows.forEach((row, index) => {
            const dateInput = row.querySelector('.multicity-date');
            const currentDate = dateInput.value;
            
            if (previousDate && currentDate < previousDate) {
                this.showFieldError(dateInput, 
                    `Row ${index + 1}: ${this.config.messages.dateSequence}`);
                isValid = false;
            }
            
            previousDate = currentDate;
        });
        
        return isValid;
    }
    
    validateRouteContinuity(rows) {
        if (!this.enableContinuityCheck) return true;
        
        let isValid = true;
        let previousToValue = null;
        let previousToText = null;
        
        rows.forEach((row, index) => {
            if (index === 0) {
                const toCity = row.querySelector('.to-city');
                previousToValue = toCity.value;
                previousToText = toCity.options[toCity.selectedIndex]?.text || '';
                return;
            }
            
            const fromCity = row.querySelector('.from-city');
            const fromValue = fromCity.value;
            const fromText = fromCity.options[fromCity.selectedIndex]?.text || '';
            
            if (previousToValue && fromValue !== previousToValue) {
                this.showFieldError(fromCity, 
                    `Row ${index + 1}: "From" location (${fromText}) must match the previous row's "To" location (${previousToText}). ${this.config.messages.routeContinuity}`);
                isValid = false;
            }
            
            const toCity = row.querySelector('.to-city');
            previousToValue = toCity.value;
            previousToText = toCity.options[toCity.selectedIndex]?.text || '';
        });
        
        return isValid;
    }
    
    // Error handling methods
    showFieldError(element, message) {
        this.clearFieldError(element);
        
        // Add error class to element
        element.classList.add('is-invalid');
        
        // Create error message element
        const errorDiv = document.createElement('div');
        errorDiv.className = 'invalid-feedback d-block';
        errorDiv.textContent = message;
        errorDiv.setAttribute('data-error-for', element.id || element.name);
        
        // Insert error message after the element
        element.parentNode.appendChild(errorDiv);
    }
    
    clearFieldError(element) {
        element.classList.remove('is-invalid');
        const existingError = element.parentNode.querySelector(`[data-error-for="${element.id || element.name}"]`);
        if (existingError) {
            existingError.remove();
        }
    }
    
    clearAllErrors() {
        const container = document.getElementById(this.containerId);
        if (!container) return;
        
        container.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
        container.querySelectorAll('.invalid-feedback').forEach(el => el.remove());
    }
    
    // Form manipulation methods
    addMulticityRow() {
        const container = document.getElementById('multicityContainer');
        if (!container) return false;
        
        const rows = container.querySelectorAll('.multicity-row');
        
        if (rows.length >= this.maxRows) {
            alert(this.config.messages.maxRowsReached);
            return false;
        }
        
        const lastRow = rows[rows.length - 1];
        const lastToValue = lastRow.querySelector('.to-city').value;
        
        if (!lastToValue) {
            alert(this.config.messages.completeCurrentRow);
            return false;
        }
        
        const newRowIndex = rows.length;
        const newRow = this.createMulticityRow(newRowIndex, lastToValue);
        container.appendChild(newRow);
        
        this.updateRemoveButtons();
        this.clearValidationResults();
        
        console.log('Added new multicity row:', newRowIndex);
        return true;
    }
    
    createMulticityRow(index, defaultFromCity = '') {
        const rowHtml = `
            <div class="multicity-row" data-row="${index}">
                <div class="row">
                    <div class="col-md-3 mb-3">
                        <label class="form-label">Date <span class="text-danger">*</span></label>
                        <input type="date" class="form-control multicity-date" name="multicity_date[]">
                    </div>
                    <div class="col-md-3 mb-3">
                        <label class="form-label">From <span class="text-danger">*</span></label>
                        <select class="form-select from-city" name="multicity_from[]">
                            <option value="">Select</option>
                        </select>
                    </div>
                    <div class="col-md-3 mb-3">
                        <label class="form-label">To <span class="text-danger">*</span></label>
                        <select class="form-select to-city" name="multicity_to[]">
                            <option value="">Select</option>
                        </select>
                    </div>
                    <div class="col-md-2 mb-3">
                        <label class="form-label">Distance (KM)</label>
                        <input type="number" class="form-control distance" name="multicity_distance[]" step="0.1" readonly>
                    </div>
                    <div class="col-md-1 mb-3">
                        <label class="form-label">&nbsp;</label>
                        <button type="button" class="btn btn-danger btn-sm remove-multicity-row w-100">
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
                </div>
                ${this.enableSightseeing ? this.getSightseeingHtml(index) : ''}
            </div>
        `;
        
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = rowHtml;
        const newRow = tempDiv.firstElementChild;
        
        // Populate city options from existing row
        this.populateCityOptions(newRow, defaultFromCity);
        
        // Bind events for new row
        this.bindRowEvents(newRow);
        
        return newRow;
    }
    
    populateCityOptions(newRow, defaultFromCity = '') {
        const existingRow = document.querySelector('.multicity-row');
        if (!existingRow) return;
        
        const existingFromSelect = existingRow.querySelector('.from-city');
        const existingToSelect = existingRow.querySelector('.to-city');
        
        const newFromSelect = newRow.querySelector('.from-city');
        const newToSelect = newRow.querySelector('.to-city');
        
        // Copy options from existing selects
        if (existingFromSelect && newFromSelect) {
            newFromSelect.innerHTML = existingFromSelect.innerHTML;
            if (defaultFromCity) {
                newFromSelect.value = defaultFromCity;
            }
        }
        
        if (existingToSelect && newToSelect) {
            newToSelect.innerHTML = existingToSelect.innerHTML;
        }
    }
    
    removeMulticityRow(rowElement) {
        const container = document.getElementById('multicityContainer');
        if (!container) return false;
        
        const rows = container.querySelectorAll('.multicity-row');
        
        if (rows.length <= 1) {
            alert(this.config.messages.minRowsRequired);
            return false;
        }
        
        rowElement.remove();
        this.updateRemoveButtons();
        this.clearValidationResults();
        
        console.log('Removed multicity row');
        return true;
    }
    
    updateRemoveButtons() {
        const rows = document.querySelectorAll('.multicity-row');
        rows.forEach((row, index) => {
            const removeBtn = row.querySelector('.remove-multicity-row');
            if (removeBtn) {
                removeBtn.style.display = rows.length > 1 ? 'block' : 'none';
            }
        });
    }
    
    // Route validation
    validateRoute() {
        console.log('Starting route validation...');
        
        const btn = document.getElementById('validateMulticityBtn');
        if (!btn) return false;
        
        const originalText = btn.innerHTML;
        
        // Clear previous errors
        this.clearAllErrors();
        
        // Validate pickup city
        if (!this.validatePickupCity()) {
            return false;
        }
        
        // Get all rows
        const rows = Array.from(document.querySelectorAll('.multicity-row'));
        if (rows.length === 0) {
            alert('No multicity rows found');
            return false;
        }
        
        let allValid = true;
        const errors = [];
        
        // Validate each row
        rows.forEach((row, index) => {
            if (!this.validateMulticityRow(row, index)) {
                allValid = false;
                errors.push(`Row ${index + 1} has validation errors`);
            }
        });
        
        // Validate date sequence
        if (!this.validateDateSequence(rows)) {
            allValid = false;
            errors.push('Date sequence validation failed');
        }
        
        // Validate route continuity if enabled
        if (!this.validateRouteContinuity(rows)) {
            allValid = false;
            errors.push('Route continuity validation failed');
        }
        
        if (!allValid) {
            if (errors.length > 0) {
                const errorMessage = this.config.messages.validationFailed + ':\n\n' + errors.join('\n');
                alert(errorMessage);
            }
            return false;
        }
        
        // Show loading state
        btn.innerHTML = '<i class="bi bi-hourglass-split"></i> Validating...';
        btn.disabled = true;
        
        // Simulate validation process
        setTimeout(() => {
            btn.innerHTML = originalText;
            btn.disabled = false;
            this.showValidationResults(true, rows);
        }, this.config.timing.validationDelay);
        
        return true;
    }
    
    showValidationResults(success, rows = []) {
        const resultsDiv = document.getElementById('validationResults');
        if (!resultsDiv) return;
        
        if (success) {
            let resultHtml = `
                <div class="alert alert-success">
                    <h6><i class="bi bi-check-circle me-2"></i>Validation Successful!</h6>
                    <div class="route-summary mt-3">
                        <strong>Route Summary:</strong><br>
            `;
            
            rows.forEach((row, index) => {
                const date = row.querySelector('.multicity-date').value;
                const fromText = row.querySelector('.from-city option:checked')?.text || 'Unknown';
                const toText = row.querySelector('.to-city option:checked')?.text || 'Unknown';
                
                resultHtml += `
                    <div class="route-item">
                        <strong>Day ${index + 1}:</strong> ${fromText} → ${toText} 
                        <small class="text-muted">(${date})</small>
                    </div>
                `;
            });
            
            resultHtml += `
                    </div>
                    <p class="mb-0 mt-2">${this.config.messages.validationSuccess}</p>
                </div>
            `;
            
            resultsDiv.innerHTML = resultHtml;
            
            // Update search button if it exists
            const searchBtn = document.getElementById('searchCabsBtn');
            if (searchBtn) {
                searchBtn.classList.remove('btn-primary');
                searchBtn.classList.add('btn-success');
                searchBtn.innerHTML = '<i class="bi bi-check-circle"></i> Validation Passed - Search Vehicles';
            }
            
        } else {
            resultsDiv.innerHTML = `
                <div class="alert alert-danger">
                    <h6><i class="bi bi-exclamation-triangle me-2"></i>Validation Failed</h6>
                    <p class="mb-0">Please check the form for errors and try again.</p>
                </div>
            `;
        }
        
        resultsDiv.style.display = 'block';
    }
    
    clearValidationResults() {
        const resultsDiv = document.getElementById('validationResults');
        if (resultsDiv) {
            resultsDiv.style.display = 'none';
        }
        
        // Reset search button if it exists
        const searchBtn = document.getElementById('searchCabsBtn');
        if (searchBtn) {
            searchBtn.classList.remove('btn-success');
            searchBtn.classList.add('btn-primary');
            searchBtn.innerHTML = '<i class="bi bi-search"></i> Search Vehicles';
        }
    }
    
    // Event binding
    bindCoreEvents() {
        // Add row button
        const addBtn = document.getElementById('addMulticityRowBtn');
        if (addBtn) {
            // Remove existing handlers to prevent duplicates
            addBtn.removeEventListener('click', this.handleAddRow);
            this.handleAddRow = () => this.addMulticityRow();
            addBtn.addEventListener('click', this.handleAddRow);
        }
        
        // Validate button
        const validateBtn = document.getElementById('validateMulticityBtn');
        if (validateBtn) {
            // Remove existing handlers to prevent duplicates
            validateBtn.removeEventListener('click', this.handleValidateRoute);
            this.handleValidateRoute = () => this.validateRoute();
            validateBtn.addEventListener('click', this.handleValidateRoute);
        }
        
        // Pickup city change
        const pickupCity = document.getElementById('multicity_pickup_city');
        if (pickupCity) {
            pickupCity.addEventListener('change', () => this.clearValidationResults());
        }
        
        // Bind events for existing rows
        document.querySelectorAll('.multicity-row').forEach(row => {
            this.bindRowEvents(row);
        });
    }
    
    bindRowEvents(row) {
        // Remove button
        const removeBtn = row.querySelector('.remove-multicity-row');
        if (removeBtn) {
            removeBtn.addEventListener('click', () => this.removeMulticityRow(row));
        }
        
        // Date validation
        const dateInput = row.querySelector('.multicity-date');
        if (dateInput) {
            dateInput.addEventListener('blur', () => this.validateDate(dateInput));
            dateInput.addEventListener('change', () => this.clearValidationResults());
        }
        
        // City validation
        const fromCity = row.querySelector('.from-city');
        const toCity = row.querySelector('.to-city');
        
        if (fromCity) {
            fromCity.addEventListener('change', () => {
                this.clearFieldError(fromCity);
                this.clearValidationResults();
            });
        }
        
        if (toCity) {
            toCity.addEventListener('change', () => {
                this.clearFieldError(toCity);
                this.clearValidationResults();
            });
        }
    }
    
    setupValidation() {
        // Any additional setup can go here
        console.log('MulticityValidator setup complete');
    }
    
    // Sightseeing integration placeholder (for extension)
    getSightseeingHtml(index) {
        // This will be overridden by the sightseeing extension
        return '';
    }
}

// Export for use in other scripts
if (typeof window !== 'undefined') {
    window.MulticityValidator = MulticityValidator;
}