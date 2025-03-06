from flask import Flask, request, jsonify
from ai_processor import generate_summary_and_questions
import time
import io
from pdf2image import convert_from_bytes
import pytesseract
import fitz  # PyMuPDF
import os
from pdf_api import process_document_with_document_ai

app = Flask(__name__)

# Configuration for Document AI
GOOGLE_PROJECT_ID = os.getenv("GOOGLE_PROJECT_ID", "your-project-id")
GOOGLE_LOCATION = os.getenv("GOOGLE_LOCATION", "us") 
GOOGLE_PROCESSOR_ID = os.getenv("GOOGLE_PROCESSOR_ID", "your-processor-id")

# Flag to enable/disable external API (for testing/development)
USE_EXTERNAL_API = os.getenv("USE_EXTERNAL_API", "false").lower() == "true"

# Add CORS support
@app.after_request
def add_cors_headers(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
    return response

@app.route('/process', methods=['POST', 'OPTIONS'])
def process_text():
    if request.method == 'OPTIONS':
        # Handle preflight request
        return jsonify({}), 200
        
    try:
        data = request.json
        
        # Check if we're receiving raw text or a PDF file for processing
        if 'text' in data:
            text = data.get('text')
            
            if not text:
                return jsonify({"error": "No text provided"}), 400
                
            # Process the text directly
            return process_raw_text(text)
        
        elif 'pdf_base64' in data:
            # Process PDF file uploaded as base64
            pdf_base64 = data.get('pdf_base64')
            if not pdf_base64:
                return jsonify({"error": "No PDF data provided"}), 400
                
            import base64
            pdf_bytes = base64.b64decode(pdf_base64.split(',')[1] if ',' in pdf_base64 else pdf_base64)
            
            # Extract text from PDF using multiple methods
            return process_pdf(pdf_bytes)
            
        else:
            return jsonify({"error": "No text or PDF provided"}), 400
            
    except Exception as e:
        print(f"Error processing request: {str(e)}")
        return jsonify({
            "error": str(e),
            "summary": "An error occurred while processing the document.",
            "questions": ["Processing error. Please try again with a smaller document."]
        }), 500

def process_raw_text(text):
    """Process text that's already been extracted"""
    start_time = time.time()
    print(f"Processing text of length: {len(text)}")
    
    # Limit text size for better performance
    MAX_TEXT_LENGTH = 100000  # 100k characters max
    if len(text) > MAX_TEXT_LENGTH:
        text = text[:MAX_TEXT_LENGTH]
        print(f"Text truncated to {MAX_TEXT_LENGTH} characters")
    
    # Process the text with AI
    result = generate_summary_and_questions(text)
    
    # Log processing time
    processing_time = time.time() - start_time
    print(f"Processing completed in {processing_time:.2f} seconds")
    
    return jsonify(result)

def process_pdf(pdf_bytes):
    """Process a PDF file using multiple extraction methods"""
    start_time = time.time()
    print("Processing PDF...")
    
    # Try multiple methods to extract text
    text = ""
    extraction_method = "Not determined"
    
    # Method 1: PyMuPDF (fastest and most reliable for text-based PDFs)
    try:
        print("Trying PyMuPDF extraction...")
        text = extract_text_with_pymupdf(pdf_bytes)
        print(f"PyMuPDF extracted {len(text)} characters")
        
        # If we got a reasonable amount of text, use it
        if len(text.strip()) > 200:
            print("Using PyMuPDF extraction results")
            extraction_method = "PyMuPDF"
    except Exception as e:
        print(f"PyMuPDF extraction failed: {str(e)}")
    
    # Method 2: OCR using Tesseract (for image-based PDFs)
    if len(text.strip()) < 200:
        try:
            print("Trying OCR extraction...")
            ocr_text = extract_text_with_ocr(pdf_bytes)
            print(f"OCR extracted {len(ocr_text)} characters")
            
            # If OCR got more text, use that instead
            if len(ocr_text.strip()) > len(text.strip()) or len(text.strip()) < 200:
                text = ocr_text
                extraction_method = "Tesseract OCR"
                print("Using OCR extraction results")
        except Exception as e:
            print(f"OCR extraction failed: {str(e)}")
    
    # Method 3: External API (if enabled and other methods didn't work well)
    if USE_EXTERNAL_API and len(text.strip()) < 200:
        try:
            print("Trying external Document AI API...")
            api_text = process_document_with_document_ai(
                pdf_bytes, 
                GOOGLE_PROJECT_ID, 
                GOOGLE_LOCATION, 
                GOOGLE_PROCESSOR_ID
            )
            print(f"Document AI API extracted {len(api_text)} characters")
            
            if len(api_text.strip()) > len(text.strip()):
                text = api_text
                extraction_method = "Google Document AI"
                print("Using Document AI API extraction results")
        except Exception as e:
            print(f"Document AI API extraction failed: {str(e)}")
    
    # If we still don't have enough text, return error
    if len(text.strip()) < 100:
        return jsonify({
            "error": "Could not extract sufficient text from the PDF",
            "summary": "The PDF appears to be image-based, encrypted, or corrupted. Try a different PDF or convert it to text first.",
            "questions": ["Could not generate questions from this document."]
        }), 400
    
    # Process the extracted text
    processing_time = time.time() - start_time
    print(f"PDF text extraction completed in {processing_time:.2f} seconds using {extraction_method}")
    
    # Process text and add extraction method info
    result = generate_summary_and_questions(text)
    result["extraction_method"] = extraction_method
    
    return jsonify(result)

def extract_text_with_pymupdf(pdf_bytes):
    """Extract text from PDF using PyMuPDF (fitz)"""
    text = ""
    
    # Open the PDF from memory
    pdf_document = fitz.open("pdf", pdf_bytes)
    
    # Process up to 50 pages
    num_pages = min(pdf_document.page_count, 50)
    
    # Extract text from each page
    for page_num in range(num_pages):
        page = pdf_document[page_num]
        text += page.get_text() + "\n\n"
    
    pdf_document.close()
    return text

def extract_text_with_ocr(pdf_bytes):
    """Extract text from PDF using OCR"""
    text = ""
    
    try:
        # Convert PDF pages to images
        images = convert_from_bytes(
            pdf_bytes,
            dpi=300,  # Higher DPI for better OCR quality
            fmt="jpeg",
            thread_count=2,  # Use multiple threads for faster conversion
            grayscale=False,
            size=(1000, None)  # Scale width to 1000px, maintain aspect ratio
        )
        
        # Limit to first 10 pages for performance reasons
        for i, image in enumerate(images[:10]):
            print(f"OCR processing page {i+1}...")
            # Perform OCR on the image
            page_text = pytesseract.image_to_string(image, lang='eng')
            text += page_text + "\n\n"
            
    except Exception as e:
        print(f"OCR processing error: {str(e)}")
        raise
        
    return text

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=False)