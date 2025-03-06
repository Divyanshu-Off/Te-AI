import './style.css';

document.getElementById('processBtn').addEventListener('click', async () => {
    const fileInput = document.getElementById('fileInput');
    const summaryDiv = document.getElementById('summary');
    const questionsList = document.getElementById('questions');
    const loadingSpinner = document.getElementById('loadingSpinner');
    const statusMessage = document.getElementById('statusMessage');

    if (fileInput.files.length === 0) {
        alert('Please upload a PDF file first!');
        return;
    }

    // Reset UI
    summaryDiv.innerHTML = '';
    questionsList.innerHTML = '';
    updateStatus('Starting to process PDF...');

    // Show loading spinner
    loadingSpinner.style.display = 'block';
    
    try {
        const file = fileInput.files[0];
        
        // Check file size and warn if too large
        if (file.size > 10 * 1024 * 1024) { // 10MB
            if (!confirm('This file is large and may take longer to process. Continue?')) {
                loadingSpinner.style.display = 'none';
                summaryDiv.innerHTML = '';
                updateStatus('');
                return;
            }
        }
        
        updateStatus('Reading file...');
        
        // Read file as base64
        const base64Data = await readFileAsBase64(file);
        updateStatus('Uploading PDF for server-side processing...');
        
        // Send PDF to server for processing
        const result = await sendPDFToBackend(base64Data);
        
        // Show extraction method if available
        if (result.extraction_method) {
            updateStatus(`PDF processed using: ${result.extraction_method}`);
            setTimeout(() => updateStatus(''), 5000);
        } else {
            updateStatus('');
        }
        
        // Show Summary
        summaryDiv.innerHTML = `<p>${result.summary}</p>`;

        // Show Questions
        questionsList.innerHTML = result.questions
            .filter(q => q && q.trim().length > 0) // Filter out empty questions
            .map(q => `<li>${q}</li>`)
            .join('');

    } catch (error) {
        console.error('Error processing PDF:', error);
        summaryDiv.innerHTML = `<p>Error processing PDF: ${error.message || 'Unknown error'}</p>`;
        questionsList.innerHTML = '';
        updateStatus('');
    } finally {
        loadingSpinner.style.display = 'none';
    }
});

// Helper function to update status message
function updateStatus(message) {
    const statusMessage = document.getElementById('statusMessage');
    if (statusMessage) {
        statusMessage.textContent = message;
    }
}

// Read file as base64
function readFileAsBase64(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => {
            const base64String = reader.result;
            resolve(base64String);
        };
        reader.onerror = (error) => reject(new Error(`File reading failed: ${error.message}`));
        reader.readAsDataURL(file);
    });
}

// Send PDF to backend
async function sendPDFToBackend(base64Data) {
    try {
        const response = await fetch('http://localhost:5000/process', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ pdf_base64: base64Data }),
            signal: AbortSignal.timeout(120000) // 2 minute timeout (OCR can take time)
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `Server responded with ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('Backend processing error:', error);
        throw error;
    }
}