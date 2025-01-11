async function handleSubmit(event) {
    event.preventDefault();
    
    // Get form values
    const formData = {
        title: document.getElementById('title').value.trim(),
        website: document.getElementById('website').value.trim(),
        description: document.getElementById('description').value.trim(),
        notes: document.getElementById('notes').value.trim(),
        email: document.getElementById('email').value.trim(),
        contact: document.getElementById('contact').value.trim(),
        contractAddresses: document.getElementById('contractAddresses').value.trim(),
        isTest: document.getElementById('title').value.toLowerCase().includes('test')
    };
    
    // Validation
    const validationErrors = [];
    
    if (!formData.title) validationErrors.push('Project Title is required');
    if (!formData.website) validationErrors.push('Website URL is required');
    if (!formData.description) validationErrors.push('Description is required');
    if (!formData.contact) validationErrors.push('Contact information is required');
    
    // Email validation
    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    if (!formData.email) {
        validationErrors.push('Email address is required');
    } else if (!emailRegex.test(formData.email)) {
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
        const successMessage = document.getElementById('successMessage');
        successMessage.style.display = 'block';
        
        setTimeout(() => {
            successMessage.style.display = 'none';
        }, 5000);
        
        // Clear form
        event.target.reset();
        
    } catch (error) {
        console.error('Error:', error);
        alert('There was an error submitting your project. Please try again.');
    }
}

// Add event listener to form
document.getElementById('projectForm').addEventListener('submit', handleSubmit);
