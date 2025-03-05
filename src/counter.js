// src/counter.js

// Optional: Counter functionality (can be removed if not needed)
export function setupCounter(element) {
  let counter = 0;
  const setCounter = (count) => {
    counter = count;
    element.innerHTML = `count is ${counter}`;
  };
  element.addEventListener('click', () => setCounter(counter + 1));
  setCounter(0);
}

// Function to generate a summary and questions from the extracted text
export function generateSummaryAndQuestions(text) {
  // Split text into sentences
  const sentences = text.split('.').filter(s => s.trim().length > 0);

  // Generate a summary by taking the first few sentences
  const summary = sentences.slice(0, 3).join('. ') + '.';

  // Generate questions based on the content
  const questions = [
    "What is the main topic discussed in the document?",
    "Can you summarize the key points in one sentence?",
    "What are the two most important ideas presented?",
    "How does the document suggest applying these concepts in a classroom setting?",
    "What questions would you ask students to test their understanding of this material?"
  ];

  return { summary, questions };
}