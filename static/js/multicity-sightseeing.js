/**
 * Multicity Sightseeing Extension
 * Extends the core MulticityValidator with sightseeing functionality for the Home page
 */

class MulticitySightseeingExtension extends MulticityValidator {
    constructor(options = {}) {
        super({
            ...options, 
            enableSightseeing: true,
            enableContinuityCheck: true,
            enableCircularRouteCheck: true
        });
        
        this.sightseeingData = new Map(); // Store sightseeing data per row
        this.initSightseeing();
    }
    
    initSightseeing() {
        console.log('Initializing sightseeing extension...');
        this.bindSightseeingEvents();
        this.initExistingSightseeingSections();
    }
    
    // Override addMulticityRow to include sightseeing functionality
    addMulticityRow() {
        const success = super.addMulticityRow();
        if (success) {
            this.initSightseeingForNewRow();
        }
        return success;
    }
    
    // Override createMulticityRow to include sightseeing HTML
    createMulticityRow(index, defaultFromCity = '') {
        const newRow = super.createMulticityRow(index, defaultFromCity);
        
        // Initialize sightseeing for this row
        this.initSightseeingForRow(newRow, index);
        
        return newRow;
    }
    
    // Generate sightseeing HTML for a row
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
                                           name="sightseeing_enabled[]" value="1" data-row="${index}">
                                    <label class="form-check-label">
                                        <strong>Include Local Sightseeing</strong>
                                        <small class="text-muted d-block">Add sightseeing distance to total trip</small>
                                    </label>
                                </div>
                                <div class="sightseeing-details" style="display: none;">
                                    <div class="row">
                                        <div class="col-md-8">
                                            <label class="form-label">Tourist Places:</label>
                                            <div class="tourist-places-list" data-row="${index}">
                                                <div class="text-muted">Select a destination city to see available tourist places</div>
                                            </div>
                                        </div>
                                        <div class="col-md-4">
                                            <label class="form-label">Sightseeing Distance:</label>
                                            <div class="sightseeing-distance-display">
                                                <span class="badge bg-info fs-6">
                                                    <span class="sightseeing-km" data-row="${index}">0</span> KM
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
    
    // Initialize sightseeing for existing rows
    initExistingSightseeingSections() {
        document.querySelectorAll('.multicity-row').forEach((row, index) => {
            this.initSightseeingForRow(row, index);
        });
    }
    
    // Initialize sightseeing for a specific row
    initSightseeingForRow(row, index) {
        const sightseeingSection = row.querySelector('.sightseeing-section');
        if (!sightseeingSection) return;
        
        // Initialize sightseeing data for this row
        this.sightseeingData.set(index, {
            enabled: false,
            selectedPlaces: [],
            totalDistance: 0
        });
        
        this.bindSightseeingRowEvents(row, index);
        this.updateSightseeingVisibility(row);
    }
    
    // Initialize sightseeing for newly added row
    initSightseeingForNewRow() {
        const rows = document.querySelectorAll('.multicity-row');
        const lastRow = rows[rows.length - 1];
        const lastIndex = rows.length - 1;
        
        this.initSightseeingForRow(lastRow, lastIndex);
        console.log('Initialized sightseeing for new row:', lastIndex);
    }
    
    // Bind sightseeing events for all rows
    bindSightseeingEvents() {
        // Use event delegation for dynamic content
        document.addEventListener('change', (e) => {
            if (e.target.classList.contains('sightseeing-checkbox')) {
                const row = e.target.closest('.multicity-row');
                const rowIndex = parseInt(e.target.getAttribute('data-row')) || 0;
                this.toggleSightseeingDetails(row, rowIndex, e.target.checked);
            }
        });
        
        document.addEventListener('change', (e) => {
            if (e.target.classList.contains('tourist-place-checkbox')) {
                const row = e.target.closest('.multicity-row');
                const rowIndex = parseInt(e.target.getAttribute('data-row')) || 0;
                this.updateSightseeingDistance(row, rowIndex);
            }
        });
    }
    
    // Bind sightseeing events for a specific row
    bindSightseeingRowEvents(row, index) {
        const sightseeingCheckbox = row.querySelector('.sightseeing-checkbox');
        if (sightseeingCheckbox) {
            sightseeingCheckbox.setAttribute('data-row', index);
        }
        
        // Monitor city changes to update tourist places
        const toCity = row.querySelector('.to-city');
        if (toCity) {
            toCity.addEventListener('change', () => {
                this.updateTouristPlaces(row, index);
                this.updateSightseeingVisibility(row);
            });
        }
    }
    
    // Toggle sightseeing details visibility
    toggleSightseeingDetails(row, rowIndex, enabled) {
        const detailsDiv = row.querySelector('.sightseeing-details');
        if (!detailsDiv) return;
        
        detailsDiv.style.display = enabled ? 'block' : 'none';
        
        // Update sightseeing data
        const data = this.sightseeingData.get(rowIndex) || {};
        data.enabled = enabled;
        this.sightseeingData.set(rowIndex, data);
        
        if (enabled) {
            this.loadTouristPlaces(row, rowIndex);
        } else {
            // Clear sightseeing data when disabled
            data.selectedPlaces = [];
            data.totalDistance = 0;
            this.updateSightseeingDistanceDisplay(row, rowIndex, 0);
        }
        
        console.log(`Sightseeing ${enabled ? 'enabled' : 'disabled'} for row ${rowIndex}`);
    }
    
    // Update sightseeing visibility based on city selection
    updateSightseeingVisibility(row) {
        const toCity = row.querySelector('.to-city');
        const sightseeingSection = row.querySelector('.sightseeing-section');
        
        if (!toCity || !sightseeingSection) return;
        
        // Show sightseeing section only if a destination city is selected
        if (toCity.value) {
            sightseeingSection.style.display = 'block';
        } else {
            sightseeingSection.style.display = 'none';
            // Reset sightseeing checkbox when hidden
            const checkbox = sightseeingSection.querySelector('.sightseeing-checkbox');
            if (checkbox) {
                checkbox.checked = false;
                this.toggleSightseeingDetails(row, parseInt(checkbox.getAttribute('data-row')) || 0, false);
            }
        }
    }
    
    // Load tourist places for a destination
    loadTouristPlaces(row, rowIndex) {
        const toCity = row.querySelector('.to-city');
        const touristPlacesList = row.querySelector('.tourist-places-list');
        
        if (!toCity || !touristPlacesList || !toCity.value) {
            touristPlacesList.innerHTML = '<div class="text-muted">Select a destination city to see available tourist places</div>';
            return;
        }
        
        const cityId = toCity.value;
        const cityName = toCity.options[toCity.selectedIndex].text;
        
        // Show loading state
        touristPlacesList.innerHTML = '<div class="text-muted"><i class="bi bi-hourglass-split"></i> Loading tourist places...</div>';
        
        // Simulate API call to load tourist places
        // In real implementation, this would be an AJAX call
        setTimeout(() => {
            this.renderTouristPlaces(touristPlacesList, rowIndex, cityId, cityName);
        }, 500);
    }
    
    // Render tourist places list
    renderTouristPlaces(container, rowIndex, cityId, cityName) {
        // Mock tourist places data - in real implementation, this would come from API
        const mockTouristPlaces = [
            { id: 1, name: `${cityName} Fort`, distance: 5 },
            { id: 2, name: `${cityName} Museum`, distance: 3 },
            { id: 3, name: `${cityName} Temple`, distance: 7 },
            { id: 4, name: `${cityName} Market`, distance: 2 },
            { id: 5, name: `${cityName} Lake`, distance: 10 }
        ];
        
        let html = '<div class="tourist-places-grid">';
        
        mockTouristPlaces.forEach(place => {
            html += `
                <div class="form-check">
                    <input class="form-check-input tourist-place-checkbox" type="checkbox" 
                           value="${place.id}" data-distance="${place.distance}" data-row="${rowIndex}"
                           id="place_${rowIndex}_${place.id}">
                    <label class="form-check-label" for="place_${rowIndex}_${place.id}">
                        ${place.name} <small class="text-muted">(${place.distance} km)</small>
                    </label>
                </div>
            `;
        });
        
        html += '</div>';
        container.innerHTML = html;
        
        console.log(`Loaded ${mockTouristPlaces.length} tourist places for ${cityName}`);
    }
    
    // Update tourist places when city changes
    updateTouristPlaces(row, rowIndex) {
        const sightseeingCheckbox = row.querySelector('.sightseeing-checkbox');
        if (sightseeingCheckbox && sightseeingCheckbox.checked) {
            this.loadTouristPlaces(row, rowIndex);
        }
    }
    
    // Update sightseeing distance calculation
    updateSightseeingDistance(row, rowIndex) {
        const checkboxes = row.querySelectorAll('.tourist-place-checkbox:checked');
        let totalDistance = 0;
        const selectedPlaces = [];
        
        checkboxes.forEach(checkbox => {
            const distance = parseFloat(checkbox.getAttribute('data-distance')) || 0;
            totalDistance += distance;
            selectedPlaces.push({
                id: checkbox.value,
                name: checkbox.nextElementSibling.textContent.trim(),
                distance: distance
            });
        });
        
        // Update sightseeing data
        const data = this.sightseeingData.get(rowIndex) || {};
        data.selectedPlaces = selectedPlaces;
        data.totalDistance = totalDistance;
        this.sightseeingData.set(rowIndex, data);
        
        // Update display
        this.updateSightseeingDistanceDisplay(row, rowIndex, totalDistance);
        
        console.log(`Updated sightseeing distance for row ${rowIndex}: ${totalDistance} km`);
    }
    
    // Update sightseeing distance display
    updateSightseeingDistanceDisplay(row, rowIndex, distance) {
        const distanceSpan = row.querySelector(`.sightseeing-km[data-row="${rowIndex}"]`);
        if (distanceSpan) {
            distanceSpan.textContent = distance.toFixed(1);
        }
    }
    
    // Get sightseeing data for form submission
    getSightseeingData() {
        const data = {};
        this.sightseeingData.forEach((value, key) => {
            if (value.enabled && value.selectedPlaces.length > 0) {
                data[key] = {
                    enabled: true,
                    places: value.selectedPlaces,
                    totalDistance: value.totalDistance
                };
            }
        });
        return data;
    }
    
    // Override validation to include sightseeing data
    validateRoute() {
        const isValid = super.validateRoute();
        
        if (isValid) {
            // Log sightseeing data for debugging
            const sightseeingData = this.getSightseeingData();
            if (Object.keys(sightseeingData).length > 0) {
                console.log('Sightseeing data:', sightseeingData);
            }
        }
        
        return isValid;
    }
    
    // Override showValidationResults to include sightseeing info
    showValidationResults(success, rows = []) {
        super.showValidationResults(success, rows);
        
        if (success && rows.length > 0) {
            const resultsDiv = document.getElementById('validationResults');
            if (!resultsDiv) return;
            
            // Add sightseeing summary if any sightseeing is enabled
            const sightseeingData = this.getSightseeingData();
            if (Object.keys(sightseeingData).length > 0) {
                let sightseeingHtml = '<div class="mt-3"><strong>Sightseeing Summary:</strong><br>';
                
                Object.entries(sightseeingData).forEach(([rowIndex, data]) => {
                    const rowNum = parseInt(rowIndex) + 1;
                    sightseeingHtml += `
                        <div class="sightseeing-summary-item">
                            <strong>Day ${rowNum}:</strong> ${data.places.length} places selected 
                            <small class="text-muted">(+${data.totalDistance.toFixed(1)} km)</small>
                        </div>
                    `;
                });
                
                sightseeingHtml += '</div>';
                
                // Append to existing results
                const alertDiv = resultsDiv.querySelector('.alert-success');
                if (alertDiv) {
                    alertDiv.insertAdjacentHTML('beforeend', sightseeingHtml);
                }
            }
        }
    }
}

// Export for use in other scripts
if (typeof window !== 'undefined') {
    window.MulticitySightseeingExtension = MulticitySightseeingExtension;
}