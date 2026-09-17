/**
 * Diabetes XAI Dashboard — Client-side JavaScript
 * Handles: threshold slider, form validation, override flow
 */

document.addEventListener('DOMContentLoaded', function() {
    
    // ========================
    // Threshold Slider
    // ========================
    const thresholdSlider = document.getElementById('threshold');
    const thresholdValue = document.getElementById('threshold-value');
    
    if (thresholdSlider && thresholdValue) {
        thresholdSlider.addEventListener('input', function() {
            thresholdValue.textContent = parseFloat(this.value).toFixed(2);
            
            // Color the badge based on threshold value
            const val = parseFloat(this.value);
            if (val < 0.3) {
                thresholdValue.style.background = '#22c55e';
            } else if (val > 0.7) {
                thresholdValue.style.background = '#ef4444';
            } else {
                thresholdValue.style.background = '#3b82f6';
            }
        });
    }
    
    // ========================
    // Form Validation
    // ========================
    const predictForm = document.getElementById('predict-form');
    
    if (predictForm) {
        predictForm.addEventListener('submit', function(e) {
            const age = parseFloat(document.getElementById('age').value);
            const bmi = parseFloat(document.getElementById('bmi').value);
            const hba1c = parseFloat(document.getElementById('HbA1c').value);
            const glucose = parseFloat(document.getElementById('glucose').value);
            
            if (age < 0 || age > 120) {
                alert('Please enter a valid age (0-120).');
                e.preventDefault();
                return;
            }
            if (bmi < 10 || bmi > 100) {
                alert('Please enter a valid BMI (10-100).');
                e.preventDefault();
                return;
            }
            if (hba1c < 2 || hba1c > 15) {
                alert('Please enter a valid HbA1c level (2-15).');
                e.preventDefault();
                return;
            }
            if (glucose < 50 || glucose > 500) {
                alert('Please enter a valid blood glucose level (50-500 mg/dL).');
                e.preventDefault();
                return;
            }
            
            // Show loading state
            const submitBtn = predictForm.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '⏳ Running Prediction...';
            }
        });
    }
    
    // ========================
    // Override Form Validation
    // ========================
    const overrideForm = document.getElementById('override-form');
    
    if (overrideForm) {
        overrideForm.addEventListener('submit', function(e) {
            const decision = document.getElementById('decision-input').value;
            const doctorName = document.getElementById('doctor_name').value.trim();
            
            if (!decision) {
                alert('Please select Accept or Reject before submitting.');
                e.preventDefault();
                return;
            }
            
            if (!doctorName) {
                alert('Please enter your name.');
                e.preventDefault();
                return;
            }
            
            if (decision === 'reject') {
                const reason = document.getElementById('reason').value.trim();
                if (!reason) {
                    alert('Please provide a reason for rejecting the prediction.');
                    e.preventDefault();
                    return;
                }
            }
            
            // Loading state
            const submitBtn = document.getElementById('submit-override');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '📝 Submitting...';
            }
        });
    }
    
    // ========================
    // Animate confidence bar on load
    // ========================
    const confidenceBar = document.querySelector('.confidence-bar');
    if (confidenceBar) {
        const probability = parseFloat(confidenceBar.dataset.probability || 0);
        // Start at 0 and animate to target
        confidenceBar.style.width = '0%';
        setTimeout(() => {
            confidenceBar.style.width = (probability * 100) + '%';
        }, 100);
    }
    
    // ========================
    // Smooth stat number animation
    // ========================
    const statNumbers = document.querySelectorAll('.stat-number');
    statNumbers.forEach(el => {
        const target = parseInt(el.textContent);
        if (!isNaN(target) && target > 0) {
            let current = 0;
            const step = Math.ceil(target / 30);
            const interval = setInterval(() => {
                current += step;
                if (current >= target) {
                    current = target;
                    clearInterval(interval);
                }
                el.textContent = current;
            }, 30);
        }
    });
});
