function showUpdateFields() {
    const updateType = document.getElementById('updateType').value;
    const devnetFields = document.getElementById('devnetFields');
    const detailFields = document.getElementById('detailFields');
    
    if (updateType === 'devnet') {
        devnetFields.style.display = 'block';
        detailFields.style.display = 'none';
    } else if (updateType === 'details') {
        devnetFields.style.display = 'none';
        detailFields.style.display = 'block';
    } else {
        devnetFields.style.display = 'none';
        detailFields.style.display = 'none';
    }
}

async function handleUpdateSubmit(event) {
    event.preventDefault();
    
    // Get form values
    const formData = {
        existingTitle: document.getElementById('existingTitle').value.trim(),
        updateType: document.getElementById('updateType').value,
        email: document.getElementById('updateEmail').value.trim(),
        contact: document.getElementById('updateContact').value.trim(),
        isUpdateRequest: true
    };
    
    // Add type-specific data
    if (formData.updateType === 'devnet') {
        formData.devnetStatus = document.getElementById('devnetStatus').value;
    } else if (formData.updateType === 'details') {
        formData.newWebsite = document.getElementById('newWebsite').value.trim();
        formData.newDescription = document.getElementById('newDescription').value.trim();
        formData.newContractAddresses = document.getElementById('newContractAddresses').value.trim();
    }
    
    // Validation
    const validationErrors = [];
    
    if (!formData.existingTitle) validationErrors.push('Current Project Title is required');
    if (!formData.updateType) validationErrors.push('Update Type is required');
    if (!formData.email) validationErrors.push('Email is required');
    if (!formData.contact) validationErrors.push('Contact information is required');
    
    // Email validation
    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    if (!emailRegex.test(formData.email)) {
        validationErrors.push('Please enter a valid email address');
    }
    
    if (validationErrors.length > 0) {
        alert('Please fix the following errors:\n\n' + validationErrors.join('\n'));
        return;
    }
    
    try {
        const response = await fetch('https://script.google.com/macros/s/AKfycbxWOX2vLuMjtyQLNCa3kaivPYuBPwtQjsCGnYgKlx6-tdxGm4hgNMRJGoUM938PK6aNig/exec', {
            method: 'POST',
            body: JSON.stringify(formData),
            mode: 'no-cors'
        });
        
        // Show success message
        const successMessage = document.getElementById('updateSuccessMessage');
        successMessage.style.display = 'block';
        
        setTimeout(() => {
            successMessage.style.display = 'none';
        }, 5000);
        
        // Clear form
        event.target.reset();
        // Reset hidden fields
        document.getElementById('devnetFields').style.display = 'none';
        document.getElementById('detailFields').style.display = 'none';
        
    } catch (error) {
        console.error('Error:', error);
        alert('There was an error submitting your update request. Please try again.');
    }
}

// Add event listener to form
document.getElementById('updateForm').addEventListener('submit', handleUpdateSubmit);
