// Main JavaScript file for CounselBot

// Get CSRF token from cookie
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Setup CSRF token for all AJAX requests
$(document).ready(function() {
    const csrftoken = getCookie('csrftoken');
    
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!(/^(GET|HEAD|OPTIONS|TRACE)$/.test(settings.type)) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });
});

// Handle option selection in assessment
function handleOptionSelection() {
    $('.option-item').on('click', function() {
        $(this).siblings().removeClass('selected');
        $(this).addClass('selected');
    });
}

// Submit assessment responses
// Note: Assessment submission is handled in assessment.html template
// This function is kept for compatibility but does nothing
function submitAssessment() {
    // Assessment form submission is handled in the assessment.html template
    // to avoid conflicts and ensure proper data formatting
}

// Handle profile updates
function handleProfileUpdate() {
    $('#profile-form').on('submit', function(e) {
        e.preventDefault();
        
        // Get CSRF token
        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        const formData = new FormData(this);
        const data = {};
        formData.forEach((value, key) => {
            data[key] = value;
        });
        
        // Get user's profile ID first, then update
        $.ajax({
            url: '/api/profiles/',
            method: 'GET',
            headers: {
                'X-CSRFToken': csrftoken
            },
            success: function(profiles) {
                if (profiles && profiles.length > 0) {
                    const profileId = profiles[0].id;
                    
                    // Now update the profile
                    $.ajax({
                        url: `/api/profiles/${profileId}/`,
                        method: 'PUT',
                        headers: {
                            'X-CSRFToken': csrftoken,
                            'Content-Type': 'application/json'
                        },
                        data: JSON.stringify(data),
                        success: function(response) {
                            showAlert('Profile updated successfully!', 'success');
                            // Reload page after short delay to show updated data
                            setTimeout(function() {
                                location.reload();
                            }, 1500);
                        },
                        error: function(xhr) {
                            showAlert('Error updating profile. Please try again.', 'danger');
                            console.error('Profile update error:', xhr.responseText);
                        }
                    });
                } else {
                    showAlert('Profile not found. Please try again.', 'danger');
                }
            },
            error: function(xhr) {
                showAlert('Error fetching profile. Please try again.', 'danger');
                console.error('Profile fetch error:', xhr.responseText);
            }
        });
    });
}

// Show alert messages
function showAlert(message, type) {
    const alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    $('.container').prepend(alertHtml);
    
    // Auto-dismiss after 5 seconds
    setTimeout(function() {
        $('.alert').alert('close');
    }, 5000);
}

// Initialize charts for recommendations
function initializeCharts() {
    if ($('#skills-chart').length) {
        const ctx = document.getElementById('skills-chart').getContext('2d');
        new Chart(ctx, {
            type: 'radar',
            data: {
                labels: skillLabels,
                datasets: [{
                    label: 'Your Skills',
                    data: skillScores,
                    backgroundColor: 'rgba(0, 123, 255, 0.2)',
                    borderColor: 'rgba(0, 123, 255, 1)',
                    pointBackgroundColor: 'rgba(0, 123, 255, 1)'
                }]
            },
            options: {
                scales: {
                    r: {
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
        });
    }
}

// Download assessment report
function downloadReport() {
    $('#download-report').on('click', function() {
        const reportId = $(this).data('report-id');
        
        $.ajax({
            url: `/api/report/${reportId}/download/`,
            method: 'GET',
            xhrFields: {
                responseType: 'blob'
            },
            success: function(response) {
                const url = window.URL.createObjectURL(response);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'career_assessment_report.pdf';
                a.click();
                window.URL.revokeObjectURL(url);
            },
            error: function(xhr) {
                showAlert('Error downloading report. Please try again.', 'danger');
            }
        });
    });
}

// Initialize all components
$(document).ready(function() {
    handleOptionSelection();
    submitAssessment();
    handleProfileUpdate();
    initializeCharts();
    downloadReport();
    
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}); 