import os
import json
import google.generativeai as genai

# Set up the Gemini API with your API key
# Get your API key from https://aistudio.google.com/app/apikey
api_key = os.getenv("GEMINI_API_KEY", "Your_API_Key")
genai.configure(api_key=api_key)

def generate_summary_and_questions(text, max_chunk_size=8000):
    """
    Generate summary and questions from text using Google's Gemini API.
    
    Args:
        text (str): The text to process
        max_chunk_size (int): Maximum size of text chunks to process
    
    Returns:
        dict: Dictionary containing summary and questions
    """
    if len(text) > max_chunk_size:
        chunks = chunk_text(text, max_chunk_size)
        all_results = []
        
        for chunk in chunks:
            result = process_chunk(chunk)
            all_results.append(result)
        
        combined_summary = " ".join([r["summary"] for r in all_results])
        combined_questions = []
        for r in all_results:
            combined_questions.extend(r["questions"][:2])  # Take top 2 questions from each chunk
        
        combined_questions = combined_questions[:5]
        
        return {"summary": combined_summary, "questions": combined_questions}
    else:
        return process_chunk(text)

def process_chunk(text):
    """Process a single chunk of text using Gemini 1.5 Flash API"""
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
    
    IMPORTANT: Only respond with valid JSON.
    """
    
    try:
        # Use Gemini 1.5 Flash model
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        
        response = model.generate_content(combined_prompt)
        
        result_text = response.text
        
        try:
            if "```json" in result_text:
                json_content = result_text.split("```json")[1].split("```")[0].strip()
                result = json.loads(json_content)
            elif "```" in result_text:
                json_content = result_text.split("```")[1].split("```")[0].strip()
                result = json.loads(json_content)
            else:
                result = json.loads(result_text)
                
            if "summary" not in result or "questions" not in result:
                raise ValueError("Missing required keys in response")
                
            if not isinstance(result["questions"], list):
                result["questions"] = [str(result["questions"])]
                
            while len(result["questions"]) < 5:
                result["questions"].append(f"Additional question {len(result['questions']) + 1}?")
                
            result["questions"] = result["questions"][:5]
                
            return result
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Error parsing response: {str(e)}")
            print(f"Raw response: {result_text}")
            summary = "Summary extraction failed due to formatting issues."
            questions = ["Could not generate structured questions from this text."]
            return {"summary": summary, "questions": questions}
    except Exception as e:
        print(f"Error calling Gemini API: {str(e)}")
        return {
            "summary": f"API error: {str(e)}", 
            "questions": ["API error occurred. Please check your API key and try again."]
        }

def chunk_text(text, max_size=8000):
    """Split text into chunks of maximum size while trying to preserve paragraphs"""
    chunks = []
    current_chunk = ""
    
    paragraphs = text.split('\n\n')
    
    for paragraph in paragraphs:
        if len(current_chunk) + len(paragraph) <= max_size:
            current_chunk += paragraph + '\n\n'
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            
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
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks

# Example usage
if __name__ == "__main__":
    sample_text = "This is a sample text about teaching methods. Teachers can use this to improve their classroom techniques."
    result = generate_summary_and_questions(sample_text)
    print(json.dumps(result, indent=2))
