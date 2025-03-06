from groq import Groq
import json
import os 

# Initialize Groq client
client = Groq(api_key="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")

def generate_summary_and_questions(text, max_chunk_size=8000):
    """
    Generate summary and questions from text using a faster model and combined prompt.
    
    Args:
        text (str): The text to process
        max_chunk_size (int): Maximum size of text chunks to process
    
    Returns:
        dict: Dictionary containing summary and questions
    """
    # Process text in chunks if it's too large
    if len(text) > max_chunk_size:
        chunks = chunk_text(text, max_chunk_size)
        all_results = []
        
        for chunk in chunks:
            result = process_chunk(chunk)
            all_results.append(result)
        
        # Combine results from all chunks
        combined_summary = " ".join([r["summary"] for r in all_results])
        combined_questions = []
        for r in all_results:
            combined_questions.extend(r["questions"][:2])  # Take top 2 questions from each chunk
        
        # Ensure we have exactly 5 questions total
        combined_questions = combined_questions[:5]
        
        return {"summary": combined_summary, "questions": combined_questions}
    else:
        return process_chunk(text)

def process_chunk(text):
    """Process a single chunk of text"""
    # Combined prompt for both summary and questions to reduce API calls
    combined_prompt = f"""
    Based on the following text, provide:
    1. A concise summary (max 150 words)
    2. 5 relevant questions that teachers could use

    TEXT:
    {text}
    
    FORMAT YOUR RESPONSE AS JSON:
    {{
        "summary": "your summary here",
        "questions": ["Q1", "Q2", "Q3", "Q4", "Q5"]
    }}
    """
    
    # Using a faster model (llama3-70b-8192) with higher temperature for creativity in questions
    response = client.chat.completions.create(
        model="llama3-70b-8192",  # Faster and more capable model
        messages=[{"role": "user", "content": combined_prompt}],
        temperature=0.7,  # Add some creativity for questions
        max_tokens=500,
        response_format={"type": "json_object"}  # Request JSON formatted response
    )
    
    result_text = response.choices[0].message.content
    
    try:
        # Parse the JSON response
        result = json.loads(result_text)
        # Ensure we have both keys
        if "summary" not in result or "questions" not in result:
            raise ValueError("Missing required keys in response")
        return result
    except json.JSONDecodeError:
        # Fallback if JSON parsing fails
        summary = "Summary extraction failed. Please try again with a smaller document."
        questions = ["Could not generate questions from this text."]
        return {"summary": summary, "questions": questions}

def chunk_text(text, max_size=8000):
    """Split text into chunks of maximum size while trying to preserve paragraphs"""
    chunks = []
    current_chunk = ""
    
    paragraphs = text.split('\n\n')
    
    for paragraph in paragraphs:
        if len(current_chunk) + len(paragraph) <= max_size:
            current_chunk += paragraph + '\n\n'
        else:
            # If current paragraph would exceed max size, add current chunk to results
            if current_chunk:
                chunks.append(current_chunk.strip())
            
            # Start new chunk with current paragraph
            # If paragraph itself is too large, split by sentences
            if len(paragraph) > max_size:
                sentences = paragraph.split('. ')
                current_chunk = ""
                
                for sentence in sentences:
                    if len(current_chunk) + len(sentence) <= max_size:
                        current_chunk += sentence + '. '
                    else:
                        chunks.append(current_chunk.strip())
                        current_chunk = sentence + '. '
            else:
                current_chunk = paragraph + '\n\n'
    
    # Add the last chunk if it's not empty
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks

# Example usage (for testing)
if __name__ == "__main__":
    sample_text = "This is a sample text about teaching methods. Teachers can use this to improve their classroom techniques."
    result = generate_summary_and_questions(sample_text)
    print(json.dumps(result, indent=2))