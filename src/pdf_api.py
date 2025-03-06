# Add this to a new file named pdf_api.py

from google.cloud import documentai_v1 as documentai
import os

# Set your environment variable for authentication
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "path/to/your/service-account-key.json"

def process_document_with_document_ai(content, project_id, location, processor_id):
    """
    Process a document using Google Document AI.
    
    Args:
        content: Binary content of the file to process
        project_id: Your Google Cloud project ID
        location: Location of your Document AI processor
        processor_id: ID of your Document AI processor
    
    Returns:
        Extracted text from the document
    """
    # Create a client
    client = documentai.DocumentProcessorServiceClient()

    # The full resource name of the processor
    name = f"projects/{project_id}/locations/{location}/processors/{processor_id}"

    # Create the document
    document = documentai.Document(
        content=content, mime_type="application/pdf"
    )

    # Configure the process request
    request = documentai.ProcessRequest(
        name=name,
        document=document,
    )

    # Process the document
    response = client.process_document(request=request)
    processed_document = response.document

    # Extract and return the text
    return processed_document.text