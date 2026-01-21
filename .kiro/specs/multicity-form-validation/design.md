# Multicity Form Validation - Technical Design

## Architecture Overview

This design document outlines the technical approach for standardizing multicity form validation between the Home page and Tour Planner page while preserving the unique sightseeing functionality on the Home page.

## Current State Analysis

### Form Locations and Differences
- **Home Page**: `templates/tours/home.html` - Complex form with sightseeing integration
- **Tour Planner Page**: `templates/tours/tour_planner.html` - Simple multicity form
- **Common Container**: Both use `id="multicityFields"`

### Key Differences Identified
1. **Sightseeing Integration**: Home page has complex sightseeing functionality
2. **Form Visibility**: Home page form is initially hidden, Tour Planner is always visible
3. **JavaScript Complexity**: Home page has additional event handler overrides
4. **Form Title**: Home page includes "Find a Cab - Multicity" title
5. **Validation Logic**: Similar but implemented separately in each template

## Proposed Solution Architecture

### 1. Shared Core Validation Library

```javascript
// Create: static/js/multicity-core-validation.js
class MulticityValidator {
    constructor(options = {}) {
        this.containerId = options.containerId || 'multicityFields';
        this.enableSightseeing = options.enableSightseeing || false;
        this.maxRows = options.maxRows || 10;
        this.init();
    }
    
    init() {
        this.bindCoreEvents();
        this.setupValidation();
    }
    
    // Core validation methods
    validatePickupCity() {
        const pickupCity = document.getElementById('multicity_pickup_city');
        return this.validateRequired(pickupCity, 'Please select a pickup city');
    }
    
    validateMulticityRow(rowElement) {
        const date = rowElement.querySelector('.multicity-date');
        const fromCity = rowElement.querySelector('.from-city');
        const toCity = rowElement.querySelector('.to-city');
        
        let isValid = true;
        
        // Validate date
        if (!this.validateDate(date)) isValid = false;
        
        // Validate cities
        if (!this.validateRequired(fromCity, 'Please select from city')) isValid = false;
        if (!this.validateRequired(toCity, 'Please select to city')) isValid = false;
        
        // Validate cities are different
        if (fromCity.value && toCity.value && fromCity.value === toCity.value) {
            this.showError(toCity, 'To city cannot be same as from city');
            isValid = false;
        }
        
        return isValid;
    }
    
    validateDate(dateInput) {
        if (!dateInput.value) {
            this.showError(dateInput, 'Date is required');
            return false;
        }
        
        const selectedDate = new Date(dateInput.value);
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        
        if (selectedDate < today) {
            this.showError(dateInput, 'Date cannot be in the past');
            return false;
        }
        
        this.clearError(dateInput);
        return true;
    }
    
    validateRequired(element, message) {
        if (!element.value.trim()) {
            this.showError(element, message);
            return false;
        }
        this.clearError(element);
        return true;
    }
    
    // Error handling methods
    showError(element, message) {
        this.clearError(element);
        element.classList.add('is-invalid');
        
        const errorDiv = document.createElement('div');
        errorDiv.className = 'invalid-feedback';
        errorDiv.textContent = message;
        errorDiv.setAttribute('data-error-for', element.id || element.name);
        
        element.parentNode.appendChild(errorDiv);
    }
    
    clearError(element) {
        element.classList.remove('is-invalid');
        const existingError = element.parentNode.querySelector(`[data-error-for="${element.id || element.name}"]`);
        if (existingError) {
            existingError.remove();
        }
    }
    
    clearAllErrors() {
        const container = document.getElementById(this.containerId);
        container.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
        container.querySelectorAll('.invalid-feedback').forEach(el => el.remove());
    }
    
    // Core form manipulation methods
    addMulticityRow() {
        const container = document.getElementById('multicityContainer');
        const rows = container.querySelectorAll('.multicity-row');
        
        if (rows.length >= this.maxRows) {
            alert(`Maximum ${this.maxRows} rows allowed`);
            return false;
        }
        
        const lastRow = rows[rows.length - 1];
        const lastToValue = lastRow.querySelector('.to-city').value;
        
        if (!lastToValue) {
            alert('Please complete the current row before adding a new one');
            return false;
        }
        
        const newRowIndex = rows.length;
        const newRow = this.createMulticityRow(newRowIndex, lastToValue);
        container.appendChild(newRow);
        
        this.updateRemoveButtons();
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
        
        // Set default from city if provided
        if (defaultFromCity) {
            const fromSelect = newRow.querySelector('.from-city');
            fromSelect.value = defaultFromCity;
        }
        
        // Bind events for new row
        this.bindRowEvents(newRow);
        
        return newRow;
    }
    
    removeMulticityRow(rowElement) {
        const container = document.getElementById('multicityContainer');
        const rows = container.querySelectorAll('.multicity-row');
        
        if (rows.length <= 1) {
            alert('At least one row is required');
            return false;
        }
        
        rowElement.remove();
        this.updateRemoveButtons();
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
        const btn = document.getElementById('validateMulticityBtn');
        const originalText = btn.innerHTML;
        
        // Clear previous errors
        this.clearAllErrors();
        
        // Validate pickup city
        if (!this.validatePickupCity()) {
            return false;
        }
        
        // Validate all rows
        const rows = document.querySelectorAll('.multicity-row');
        let allValid = true;
        
        rows.forEach(row => {
            if (!this.validateMulticityRow(row)) {
                allValid = false;
            }
        });
        
        if (!allValid) {
            return false;
        }
        
        // Show loading state
        btn.innerHTML = '<i class="bi bi-hourglass-split"></i> Validating...';
        btn.disabled = true;
        
        // Simulate validation (replace with actual API call)
        setTimeout(() => {
            btn.innerHTML = originalText;
            btn.disabled = false;
            this.showValidationResults(true);
        }, 1500);
        
        return true;
    }
    
    showValidationResults(success) {
        const resultsDiv = document.getElementById('validationResults');
        if (success) {
            resultsDiv.innerHTML = `
                <div class="alert alert-success">
                    <h6><i class="bi bi-check-circle me-2"></i>Route Validated Successfully</h6>
                    <p class="mb-0">Your multicity route has been validated and is ready for booking.</p>
                </div>
            `;
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
    
    // Event binding
    bindCoreEvents() {
        // Add row button
        const addBtn = document.getElementById('addMulticityRowBtn');
        if (addBtn) {
            addBtn.addEventListener('click', () => this.addMulticityRow());
        }
        
        // Validate button
        const validateBtn = document.getElementById('validateMulticityBtn');
        if (validateBtn) {
            validateBtn.addEventListener('click', () => this.validateRoute());
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
        }
        
        // City validation
        const fromCity = row.querySelector('.from-city');
        const toCity = row.querySelector('.to-city');
        
        if (fromCity) {
            fromCity.addEventListener('change', () => this.validateMulticityRow(row));
        }
        
        if (toCity) {
            toCity.addEventListener('change', () => this.validateMulticityRow(row));
        }
    }
    
    // Sightseeing integration (for Home page only)
    getSightseeingHtml(index) {
        return `
            <div class="sightseeing-section" style="display: none;">
                <div class="row">
                    <div class="col-md-12">
                        <div class="card border-info">
                            <div class="card-header bg-light">
                                <h6 class="mb-0 text-info">
                                    <i class="bi bi-camera me-2"></i>
                                    <span class="sightseeing-title">Local Sightseeing</span>
                                </h6>
                            </div>
                            <div class="card-body">
                                <div class="form-check mb-3">
                                    <input class="form-check-input sightseeing-checkbox" type="checkbox" 
                                           name="sightseeing_enabled[]" value="1">
                                    <label class="form-check-label">
                                        <strong>Include Local Sightseeing</strong>
                                        <small class="text-muted d-block">Add sightseeing distance to total trip</small>
                                    </label>
                                </div>
                                <div class="sightseeing-details" style="display: none;">
                                    <div class="row">
                                        <div class="col-md-8">
                                            <label class="form-label">Tourist Places:</label>
                                            <div class="tourist-places-list">
                                                <!-- Tourist places will be loaded here -->
                                            </div>
                                        </div>
                                        <div class="col-md-4">
                                            <label class="form-label">Sightseeing Distance:</label>
                                            <div class="sightseeing-distance-display">
                                                <span class="badge bg-info fs-6">
                                                    <span class="sightseeing-km">0</span> KM
                                                </span>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
}
```

### 2. Sightseeing Extension (Home Page Only)

```javascript
// Create: static/js/multicity-sightseeing.js
class MulticitySightseeingExtension extends MulticityValidator {
    constructor(options = {}) {
        super({...options, enableSightseeing: true});
        this.initSightseeing();
    }
    
    initSightseeing() {
        this.bindSightseeingEvents();
    }
    
    addMulticityRow() {
        const success = super.addMulticityRow();
        if (success) {
            this.initSightseeingForNewRow();
        }
        return success;
    }
    
    bindSightseeingEvents() {
        // Bind sightseeing events for existing rows
        document.querySelectorAll('.multicity-row').forEach(row => {
            this.bindSightseeingRowEvents(row);
        });
    }
    
    bindSightseeingRowEvents(row) {
        const sightseeingCheckbox = row.querySelector('.sightseeing-checkbox');
        if (sightseeingCheckbox) {
            sightseeingCheckbox.addEventListener('change', (e) => {
                this.toggleSightseeingDetails(row, e.target.checked);
            });
        }
    }
    
    toggleSightseeingDetails(row, enabled) {
        const detailsDiv = row.querySelector('.sightseeing-details');
        if (detailsDiv) {
            detailsDiv.style.display = enabled ? 'block' : 'none';
        }
        
        if (enabled) {
            this.loadTouristPlaces(row);
        }
    }
    
    loadTouristPlaces(row) {
        // Implementation for loading tourist places
        // This preserves the existing sightseeing functionality
    }
    
    initSightseeingForNewRow() {
        const rows = document.querySelectorAll('.multicity-row');
        const lastRow = rows[rows.length - 1];
        this.bindSightseeingRowEvents(lastRow);
    }
}
```

### 3. Integration Strategy

#### Home Page Integration
```html
<!-- In templates/tours/home.html -->
<script src="{% static 'js/multicity-core-validation.js' %}"></script>
<script src="{% static 'js/multicity-sightseeing.js' %}"></script>

<script>
document.addEventListener('DOMContentLoaded', function() {
    // Initialize with sightseeing extension
    window.multicityValidator = new MulticitySightseeingExtension({
        containerId: 'multicityFields',
        maxRows: 10
    });
});
</script>
```

#### Tour Planner Integration
```html
<!-- In templates/tours/tour_planner.html -->
<script src="{% static 'js/multicity-core-validation.js' %}"></script>

<script>
document.addEventListener('DOMContentLoaded', function() {
    // Initialize with core validation only
    window.multicityValidator = new MulticityValidator({
        containerId: 'multicityFields',
        maxRows: 10
    });
});
</script>
```

## Implementation Plan

### Phase 1: Core Library Development
1. **Create Core Validation Library**
   - Implement `MulticityValidator` class with core functionality
   - Create shared validation methods
   - Implement error handling and display
   - Add form manipulation methods

2. **Create Sightseeing Extension**
   - Extend core validator for sightseeing functionality
   - Preserve existing sightseeing behavior
   - Ensure proper integration with core validation

### Phase 2: Template Updates
1. **Update Home Page**
   - Remove existing multicity JavaScript
   - Integrate new validation library with sightseeing extension
   - Test sightseeing functionality preservation
   - Verify form behavior consistency

2. **Update Tour Planner**
   - Remove existing multicity JavaScript
   - Integrate core validation library
   - Test simplified form behavior
   - Verify consistency with Home page core functionality

### Phase 3: Testing and Validation
1. **Core Functionality Testing**
   - Test identical validation behavior on both forms
   - Verify error handling consistency
   - Test form manipulation (add/remove rows)
   - Validate route validation consistency

2. **Feature-Specific Testing**
   - Test sightseeing functionality on Home page
   - Verify Tour Planner simplicity is maintained
   - Test cross-browser compatibility
   - Perform regression testing

## File Structure

```
static/
├── js/
│   ├── multicity-core-validation.js    # Core validation library
│   └── multicity-sightseeing.js        # Sightseeing extension
├── css/
│   └── multicity-forms.css             # Shared form styling (if needed)
templates/tours/
├── home.html                           # Updated with sightseeing extension
└── tour_planner.html                   # Updated with core validation
```

## Validation Consistency Matrix

| Feature | Home Page | Tour Planner | Implementation |
|---------|-----------|--------------|----------------|
| Pickup City Validation | ✓ | ✓ | Core Library |
| Date Validation | ✓ | ✓ | Core Library |
| City Selection Validation | ✓ | ✓ | Core Library |
| Add/Remove Rows | ✓ | ✓ | Core Library |
| Route Validation | ✓ | ✓ | Core Library |
| Error Display | ✓ | ✓ | Core Library |
| Sightseeing Features | ✓ | ✗ | Extension Only |

## Performance Considerations

1. **Lazy Loading**: Load sightseeing extension only on Home page
2. **Code Splitting**: Separate core validation from sightseeing features
3. **Event Optimization**: Use event delegation where appropriate
4. **Memory Management**: Proper cleanup of event listeners

## Backward Compatibility

1. **Existing APIs**: Maintain existing form submission formats
2. **Event Names**: Preserve existing custom event names if used
3. **CSS Classes**: Maintain existing CSS class names
4. **Data Attributes**: Preserve existing data attributes

## Testing Strategy

### Unit Tests
- Core validation functions
- Error handling methods
- Form manipulation methods
- Sightseeing extension methods

### Integration Tests
- Form initialization on both pages
- Cross-form validation consistency
- Sightseeing integration with core validation
- Form submission workflows

### Manual Testing
- User experience consistency
- Cross-browser compatibility
- Mobile responsiveness
- Accessibility compliance

## Success Metrics

1. **Functional Consistency**: 100% identical core validation behavior
2. **Feature Preservation**: 100% sightseeing functionality retention
3. **Code Quality**: Significant reduction in code duplication
4. **Performance**: No degradation in form response times
5. **User Experience**: Consistent behavior across both forms

## Risk Mitigation

### Technical Risks
- **Breaking Changes**: Comprehensive testing and gradual rollout
- **Performance Impact**: Optimize shared libraries and monitor performance
- **Browser Compatibility**: Test across all supported browsers

### Functional Risks
- **Sightseeing Regression**: Extensive testing of sightseeing features
- **Validation Inconsistency**: Automated tests for validation parity
- **User Experience Disruption**: Maintain identical user-facing behavior