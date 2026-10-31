// ApplyMate AI - Main Frontend JavaScript

document.addEventListener('DOMContentLoaded', function () {
    // 1. Mobile Sidebar Toggle
    const sidebar = document.getElementById('appSidebar');
    const toggleBtn = document.getElementById('sidebarToggleBtn');
    if (toggleBtn && sidebar) {
        toggleBtn.addEventListener('click', function () {
            sidebar.classList.toggle('show');
        });
    }

    // 2. Animate Circular Score Gauges
    const scoreCircles = document.querySelectorAll('.score-circle-progress');
    scoreCircles.forEach(circle => {
        const score = parseInt(circle.getAttribute('data-score') || '0', 10);
        const radius = circle.r.baseVal.value;
        const circumference = 2 * Math.PI * radius;
        
        circle.style.strokeDasharray = `${circumference} ${circumference}`;
        circle.style.strokeDashoffset = circumference;
        
        // Compute offset
        const offset = circumference - (score / 100) * circumference;
        setTimeout(() => {
            circle.style.strokeDashoffset = offset;
        }, 150);
    });

    // 3. Initialize Bootstrap Tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});

/**
 * Copies draft or plain text to user clipboard with visual confirmation.
 */
function copyToClipboard(elementId, btnElement) {
    const textElem = document.getElementById(elementId);
    if (!textElem) return;
    
    const textToCopy = textElem.innerText || textElem.value;
    navigator.clipboard.writeText(textToCopy).then(() => {
        const originalHTML = btnElement.innerHTML;
        btnElement.innerHTML = '<i class="bi bi-check2 text-success me-1"></i> Copied!';
        btnElement.classList.add('btn-light');
        
        setTimeout(() => {
            btnElement.innerHTML = originalHTML;
            btnElement.classList.remove('btn-light');
        }, 2200);
    }).catch(err => {
        console.error('Failed to copy: ', err);
        alert('Could not copy to clipboard. Please copy manually.');
    });
}

/**
 * Downloads text as a local text file.
 */
function downloadDraftAsFile(elementId, filename) {
    const textElem = document.getElementById(elementId);
    if (!textElem) return;
    
    const text = textElem.innerText || textElem.value;
    const blob = new Blob([text], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename || 'application_draft.txt';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}

/**
 * Pre-fills opportunity form with sample data for instant demos.
 */
function prefillOpportunityForm(sampleKey) {
    const samples = window.APPLYMATE_SAMPLES || {};
    const sample = samples[sampleKey];
    if (!sample) return;

    const titleInput = document.getElementById('id_title');
    const orgInput = document.getElementById('id_organization');
    const catSelect = document.getElementById('id_category');
    const locInput = document.getElementById('id_location');
    const deadInput = document.getElementById('id_deadline');
    const urlInput = document.getElementById('id_url');
    const descTextarea = document.getElementById('id_description');
    const reqTextarea = document.getElementById('id_requirements');

    if (titleInput) titleInput.value = sample.title || '';
    if (orgInput) orgInput.value = sample.organization || '';
    if (catSelect) catSelect.value = sample.category || 'internship';
    if (locInput) locInput.value = sample.location || '';
    if (deadInput) deadInput.value = sample.deadline || '';
    if (urlInput) urlInput.value = sample.url || '';
    if (descTextarea) descTextarea.value = sample.description || '';
    if (reqTextarea) reqTextarea.value = sample.requirements || '';

    // Visual pulse effect
    [titleInput, orgInput, descTextarea].forEach(el => {
        if (el) {
            el.classList.add('border-primary');
            setTimeout(() => el.classList.remove('border-primary'), 1200);
        }
    });
}
