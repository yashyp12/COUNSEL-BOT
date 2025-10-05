// Main JavaScript file for CounselBot

// Handle option selection in assessment
function handleOptionSelection() {
    $('.option-item').on('click', function() {
        $(this).siblings().removeClass('selected');
        $(this).addClass('selected');
    });
}

// Submit assessment responses
function submitAssessment() {
    $('#assessment-form').on('submit', function(e) {
        e.preventDefault();
        
        const responses = [];
        $('.question-card').each(function() {
            const questionId = $(this).data('question-id');
            const selectedOption = $(this).find('.option-item.selected').data('value');
            
            if (selectedOption) {
                responses.push({
                    question: questionId,
                    response_text: selectedOption
                });
            }
        });

        // Submit responses to API
        $.ajax({
            url: '/api/responses/',
            method: 'POST',
            data: JSON.stringify(responses),
            contentType: 'application/json',
            success: function(response) {
                window.location.href = '/recommendations/';
            },
            error: function(xhr) {
                showAlert('Error submitting responses. Please try again.', 'danger');
            }
        });
    });
}

// Handle profile updates
function handleProfileUpdate() {
    $('#profile-form').on('submit', function(e) {
        e.preventDefault();
        
        const formData = $(this).serialize();
        
        $.ajax({
            url: '/api/profiles/',
            method: 'PUT',
            data: formData,
            success: function(response) {
                showAlert('Profile updated successfully!', 'success');
            },
            error: function(xhr) {
                showAlert('Error updating profile. Please try again.', 'danger');
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