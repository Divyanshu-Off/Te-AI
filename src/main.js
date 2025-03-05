import './style.css';
import { setupCounter } from './counter.js';
import { generateSummaryAndQuestions } from './counter.js';
import * as pdfjsLib from 'pdfjs-dist';

pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';

document.getElementById('processBtn').addEventListener('click', async () => {
    const fileInput = document.getElementById('fileInput');
    const summaryDiv = document.getElementById('summary');
    const questionsList = document.getElementById('questions');
    const progressContainer = document.getElementById('progressContainer');
    const progressBar = document.getElementById('progressBar');
    const progressLabel = document.getElementById('progressLabel');
    const loadingSpinner = document.getElementById('loadingSpinner');

    if (fileInput.files.length === 0) {
        alert('Please upload a PDF file first!');
        return;
    }

    // Reset UI
    summaryDiv.innerHTML = '';
    questionsList.innerHTML = '';

    // Show progress bar and loading spinner
    progressContainer.style.display = 'block';
    loadingSpinner.style.display = 'block';
    updateProgress(0); // Start at 0%

    const file = fileInput.files[0];
    const reader = new FileReader();

    reader.onload = async function(event) {
        updateProgress(30); // Initial loading progress

        const arrayBuffer = event.target.result;
        const text = await extractTextFromPDF(arrayBuffer);
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
            loadingSpinner.style.display = 'none'; // Hide loading spinner
        }, 500);
    };

    reader.readAsArrayBuffer(file);
});

// Function to extract text from PDF using pdfjs-dist
async function extractTextFromPDF(arrayBuffer) {
    const pdf = await pdfjsLib.getDocument({ data: arrayBuffer }).promise;
    let text = '';
    for (let i = 1; i <= pdf.numPages; i++) {
        const page = await pdf.getPage(i);
        const content = await page.getTextContent();
        text += content.items.map(item => item.str).join(' ');
    }
    return text;
}

function updateProgress(value) {
    const progressBar = document.getElementById('progressBar');
    const progressLabel = document.getElementById('progressLabel');
    progressBar.value = value;
    progressLabel.textContent = value + '%';
}

setupCounter(document.querySelector('#counter'));