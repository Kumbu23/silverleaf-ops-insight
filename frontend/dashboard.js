// Global chart instance
let campusChart = null;

// Format currency for Tanzania (TZS)
function formatCurrency(value) {
    return new Intl.NumberFormat('en-US', {
        minimumFractionDigits: 0,
        maximumFractionDigits: 0,
    }).format(value);
}

// Format percentage
function formatPercent(value) {
    return (value || 0).toFixed(1) + '%';
}

// Show/hide elements
function show(elementId) {
    document.getElementById(elementId).classList.remove('hidden');
}

function hide(elementId) {
    document.getElementById(elementId).classList.add('hidden');
}

// Update dashboard with report data
function displayReport(report) {
    console.log('Report received:', report);
    
    const stats = report.overall_stats;
    
    // Update key metrics
    document.getElementById('totalDue').textContent = formatCurrency(stats.total_due);
    document.getElementById('totalPaid').textContent = formatCurrency(stats.total_paid);
    document.getElementById('collectionRate').textContent = formatPercent(stats.overall_collection_rate);
    document.getElementById('outstanding').textContent = formatCurrency(stats.overall_outstanding);
    document.getElementById('studentCount').textContent = stats.total_students;
    document.getElementById('anomalyCount').textContent = report.anomaly_count;
    
    // Update timestamp
    const timestamp = new Date(report.timestamp).toLocaleString();
    document.getElementById('reportTimestamp').textContent = `Generated: ${timestamp}`;
    
    // Populate campus table
    populateCampusTable(report.by_campus);
    
    // Update charts
    updateCampusChart(report.by_campus);
    
    // Display anomalies
    displayAnomalies(report.anomalies);
    
    // Show dashboard
    hide('uploadSection');
    hide('loadingSpinner');
    show('dashboard');
}

function populateCampusTable(campusByData) {
    const tbody = document.getElementById('campusTableBody');
    tbody.innerHTML = '';
    
    for (const [campus, data] of Object.entries(campusByData)) {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td><strong>${campus}</strong></td>
            <td>${data.student_count}</td>
            <td>${formatCurrency(data.total_due)}</td>
            <td>${formatCurrency(data.total_paid)}</td>
            <td>${formatCurrency(data.outstanding)}</td>
            <td><span class="badge ${data.collection_rate >= 80 ? 'badge-success' : 'badge-warning'}">
                ${formatPercent(data.collection_rate)}
            </span></td>
        `;
        tbody.appendChild(row);
    }
}

function updateCampusChart(campusByData) {
    const ctx = document.getElementById('campusChart');
    
    if (campusChart) {
        campusChart.destroy();
    }
    
    const campusNames = Object.keys(campusByData);
    const collectionRates = campusNames.map(campus => campusByData[campus].collection_rate);
    const outstandingAmounts = campusNames.map(campus => campusByData[campus].outstanding);
    
    campusChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: campusNames,
            datasets: [
                {
                    label: 'Collection Rate (%)',
                    data: collectionRates,
                    borderColor: '#2ecc71',
                    backgroundColor: 'rgba(46, 204, 113, 0.1)',
                    yAxisID: 'y',
                    borderWidth: 2,
                },
                {
                    label: 'Outstanding (TZS millions)',
                    data: outstandingAmounts.map(v => v / 1000000),
                    borderColor: '#e74c3c',
                    backgroundColor: 'rgba(231, 76, 60, 0.1)',
                    yAxisID: 'y1',
                    borderWidth: 2,
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                },
            },
            scales: {
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    title: { display: true, text: 'Collection Rate (%)' },
                    min: 0,
                    max: 100,
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    title: { display: true, text: 'Outstanding (Millions TZS)' },
                    grid: { drawOnChartArea: false },
                }
            }
        }
    });
}

function displayAnomalies(anomalies) {
    const container = document.getElementById('anomaliesContainer');
    
    if (anomalies.length === 0) {
        container.innerHTML = '<p class="no-anomalies">✓ No anomalies detected</p>';
        return;
    }
    
    // Group by severity
    const high = anomalies.filter(a => a.severity === 'high');
    const medium = anomalies.filter(a => a.severity === 'medium');
    
    let html = '';
    
    if (high.length > 0) {
        html += '<div class="anomaly-group"><h3>🔴 High Severity</h3>';
        high.forEach(anomaly => {
            html += renderAnomalyCard(anomaly, 'high');
        });
        html += '</div>';
    }
    
    if (medium.length > 0) {
        html += '<div class="anomaly-group"><h3>🟡 Medium Severity</h3>';
        medium.forEach(anomaly => {
            html += renderAnomalyCard(anomaly, 'medium');
        });
        html += '</div>';
    }
    
    container.innerHTML = html;
}

function renderAnomalyCard(anomaly, severity) {
    return `
        <div class="anomaly-card anomaly-${severity}">
            <div class="anomaly-header">
                <span class="anomaly-id">Student: ${anomaly.student_id}</span>
                <span class="anomaly-campus">${anomaly.campus}</span>
            </div>
            <div class="anomaly-body">
                <p><strong>Issue:</strong> ${anomaly.flag_reason}</p>
                <p><strong>Amount:</strong> TZS ${formatCurrency(anomaly.amount_due)}</p>
            </div>
        </div>
    `;
}

// Form submission
document.getElementById('uploadForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const formData = new FormData();
    const fileInput = document.getElementById('csvFile');
    formData.append('file', fileInput.files[0]);
    
    show('loadingSpinner');
    hide('errorMessage');
    
    try {
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const report = await response.json();
        displayReport(report);
    } catch (error) {
        console.error('Upload error:', error);
        show('errorMessage');
        document.getElementById('errorMessage').textContent = `Error: ${error.message}`;
        hide('loadingSpinner');
    }
});

// Load sample data
async function loadSampleData() {
    show('loadingSpinner');
    hide('errorMessage');
    
    try {
        const response = await fetch('/api/sample');
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const report = await response.json();
        displayReport(report);
    } catch (error) {
        console.error('Sample data error:', error);
        show('errorMessage');
        document.getElementById('errorMessage').textContent = `Error loading sample: ${error.message}`;
        hide('loadingSpinner');
    }
}

// Drag and drop
const fileInput = document.getElementById('csvFile');
const uploadBox = document.querySelector('.file-input-wrapper');

uploadBox.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadBox.classList.add('dragover');
});

uploadBox.addEventListener('dragleave', () => {
    uploadBox.classList.remove('dragover');
});

uploadBox.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadBox.classList.remove('dragover');
    fileInput.files = e.dataTransfer.files;
});

// Initial UI state
window.addEventListener('DOMContentLoaded', () => {
    console.log('Dashboard loaded. Ready to process fee records.');
});
