import './style.css'
import { setupCounter } from './counter.js'
import { generateSummaryAndQuestions } from './counter.js';

import { generateSummaryAndQuestions } from './counter.js';

document.getElementById('processBtn').addEventListener('click', async () => {
    const fileInput = document.getElementById('fileInput');
    const summaryDiv = document.getElementById('summary');
    const questionsList = document.getElementById('questions');
    const progressContainer = document.getElementById('progressContainer');
    const progressBar = document.getElementById('progressBar');
    const progressLabel = document.getElementById('progressLabel');

    if (fileInput.files.length === 0) {
        alert('Please upload a PDF file first!');
        return;
    }

    // Reset UI
    summaryDiv.innerHTML = '';
    questionsList.innerHTML = '';

    // Show progress bar
    progressContainer.style.display = 'block';
    updateProgress(0); // Start at 0%

    const file = fileInput.files[0];
    const reader = new FileReader();

    reader.onload = async function(event) {
        updateProgress(30); // Initial loading progress

        const text = await extractTextFromPDF(event.target.result);
        updateProgress(60); // Text extraction progress

        const { summary, questions } = generateSummaryAndQuestions(text);
        updateProgress(90); // Almost done

        // Show Summary
        summaryDiv.innerHTML = summary.split('\n').map(line => `<p>${line}</p>`).join('');

        // Show Questions
        questionsList.innerHTML = questions.map(q => `<li>${q}</li>`).join('');

        updateProgress(100); // Finished
        setTimeout(() => {
            progressContainer.style.display = 'none'; // Hide progress bar after a short delay
        }, 500);
    };

    reader.readAsArrayBuffer(file);
});

// Simulate PDF text extraction (replace this with real PDF parsing logic if needed)
async function extractTextFromPDF(arrayBuffer) {
    return new Promise((resolve) => {
        setTimeout(() => {
            resolve("This is sample text extracted from the PDF file.\nIt covers key topics for teachers.");
        }, 1500); // Simulate a 1.5 second delay for text extraction
    });
}

function updateProgress(value) {
    const progressBar = document.getElementById('progressBar');
    const progressLabel = document.getElementById('progressLabel');
    progressBar.value = value;
    progressLabel.textContent = value + '%';
}


setupCounter(document.querySelector('#counter'))
