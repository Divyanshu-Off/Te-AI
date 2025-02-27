export function setupCounter(element) {
  let counter = 0
  const setCounter = (count) => {
    counter = count
    element.innerHTML = `count is ${counter}`
  }
  element.addEventListener('click', () => setCounter(counter + 1))
  setCounter(0)
}

// Simulate AI logic for generating summary and questions
export function generateSummaryAndQuestions(text) {
  // Simple mock logic to split into summary and questions
  const sentences = text.split('.').filter(s => s.trim().length > 0);
  
  const summary = sentences.slice(0, 5).join('. ') + '.';
  
  const questions = [
      "What is the main topic discussed?",
      "Mention two key points.",
      "Summarize the content in one line.",
      "What important detail is covered in paragraph 1?",
      "List one takeaway from the text."
  ];

  return { summary, questions };
}
