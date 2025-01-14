console.log('Submit.js loaded');

function handleSubmit(event) {
    event.preventDefault();
    console.log('Form submitted - starting process');
    
    const submitButton = document.querySelector('.submit-button');
    submitButton.disabled = true;
    submitButton.textContent = 'Submitting...';
    
    const formData = {
        title: document.getElementById('title').value.trim(),
        website: document.getElementById('website').value.trim(),
        description: document.getElementById('description').value.trim(),
        notes: document.getElementById('notes').value.trim(),
        email: document.getElementById('email').value.trim(),
        contact: document.getElementById('contact').value.trim(),
        contractAddresses: document.getElementById('contractAddresses').value.trim(),
        isOnDevnet: document.getElementById('devnetStatus').value === 'true',
        isTest: document.getElementById('title').value.toLowerCase().includes('test')
    };
    
    console.log('Form data collected:', formData);
    
    try {
        // Create a temporary form
        const tempForm = document.createElement('form');
        tempForm.method = 'POST';
        tempForm.action = 'https://script.google.com/macros/s/AKfycbzuRpWeiSgEGGc22otCeQz5PWMwMSAUTi1QhRY8z79Crq90P2dHtEZSSt2MM3UHVX_wqQ/exec';
        tempForm.target = 'hidden_iframe';
        
        // Add data as hidden input
        const dataInput = document.createElement('input');
        dataInput.type = 'hidden';
        dataInput.name = 'data';
        dataInput.value = JSON.stringify(formData);
        tempForm.appendChild(dataInput);
        
        // Create hidden iframe if it doesn't exist
        let iframe = document.getElementById('hidden_iframe');
        if (!iframe) {
            iframe = document.createElement('iframe');
            iframe.name = 'hidden_iframe';
            iframe.id = 'hidden_iframe';
            iframe.style.display = 'none';
            document.body.appendChild(iframe);
        }
        
        // Add form to body and submit
        document.body.appendChild(tempForm);
        console.log('Submitting form...');
        tempForm.submit();
        
        // Cleanup
        setTimeout(() => {
            document.body.removeChild(tempForm);
        }, 500);
        
        // Show success message
        const successMessage = document.createElement('div');
        successMessage.className = 'alert success';
        successMessage.textContent = 'Project submitted successfully! We will review it shortly.';
        document.querySelector('.form-container').prepend(successMessage);
        
        // Reset form
        event.target.reset();
        
        // Remove success message after 5 seconds
        setTimeout(() => successMessage.remove(), 5000);
        
    } catch (error) {
        console.error('Submission error:', error);
        const errorMessage = document.createElement('div');
        errorMessage.className = 'alert error';
        errorMessage.textContent = 'There was an error submitting your project. Please try again.';
        document.querySelector('.form-container').prepend(errorMessage);
    } finally {
        submitButton.disabled = false;
        submitButton.textContent = 'Submit Project';
    }
}

document.getElementById('submitForm').addEventListener('submit', handleSubmit);
console.log('Event listener added to form');

// Test functions for projects.json updates
function testProjectFormat() {
  // Actual format from your projects.json
  const existingFormat = {
    "title": "MonadLogos",
    "isOnDevnet": true,
    "website": "https://monadlogos.vercel.app/",
    "description": "Mint colorful Monad Logos on devnet.",
    "notes": "",
    "contact": "SudoBug",
    "relatedContractAddresses": ["0xf1AC21c315E0345C04365B2D68a906cb2c3Cf8c6"]
  };
  
  // Test with a new submission
  const newSubmission = {
    title: "Test Project",
    website: "https://test.com",
    description: "Test Description",
    notes: "Test Notes",
    contact: "test#1234",
    contractAddresses: "0x456, 0x789",  // From form input
    isOnDevnet: true,
    isTest: true
  };
  
  // Convert submission to correct format
  const formattedProject = {
    title: newSubmission.title,
    isOnDevnet: newSubmission.isOnDevnet,
    website: newSubmission.website,
    description: newSubmission.description,
    notes: newSubmission.notes || "",
    contact: newSubmission.contact,
    relatedContractAddresses: newSubmission.contractAddresses ? 
      newSubmission.contractAddresses.split(',').map(addr => addr.trim()) : []
  };
  
  Logger.log('Existing Format Sample:');
  Logger.log(JSON.stringify(existingFormat, null, 2));
  Logger.log('\nNew Formatted Project:');
  Logger.log(JSON.stringify(formattedProject, null, 2));
  
  return formattedProject;
}

function testMergeWithExisting() {
  // Your actual first few projects
  const existingProjects = [
    {
      "title": "MonadLogos",
      "isOnDevnet": true,
      "website": "https://monadlogos.vercel.app/",
      "description": "Mint colorful Monad Logos on devnet.",
      "notes": "",
      "contact": "SudoBug",
      "relatedContractAddresses": ["0xf1AC21c315E0345C04365B2D68a906cb2c3Cf8c6"]
    },
    {
      "title": "BreakMonad",
      "isOnDevnet": false,
      "website": "https://www.breakmonad.com/",
      "description": "Click to send transactions. Mint an NFT representative of you trying to break devnet.",
      "notes": "NFT mint feature is being debugged.",
      "contact": ["saviour1001 (DC)", "vrajdesai (DC)"],
      "relatedContractAddresses": []
    }
  ];
  
  // New formatted project
  const newProject = testProjectFormat();
  
  // Merge
  existingProjects.push(newProject);
  
  Logger.log('\nUpdated projects array:');
  Logger.log(JSON.stringify(existingProjects, null, 2));
  
  return existingProjects;
}

// Helper function to format a submission into projects.json format
function formatSubmissionForJson(submission) {
  // Handle different address separators (commas, newlines, or both)
  const formatAddresses = (addressString) => {
    if (!addressString) return [];
    
    // First standardize the separators and clean up
    return addressString
      .replace(/[\n\r,]+/g, '|') // Replace all newlines and commas with a pipe
      .split('|') // Split by pipe
      .map(addr => addr.trim()) // Trim whitespace
      .filter(addr => addr.length > 0 && addr.startsWith('0x')); // Remove empty strings and validate format
  };

  return {
    title: submission.title,
    isOnDevnet: submission.isOnDevnet,
    website: submission.website,
    description: submission.description,
    notes: submission.notes || "",
    contact: submission.contact,
    relatedContractAddresses: formatAddresses(submission.contractAddresses)
  };
}
