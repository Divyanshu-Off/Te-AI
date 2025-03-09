# Te-AI

A web-based AI project that summarizes PDFs and generates quizzes to help teachers efficiently utilize study materials and enhance student understanding with key points.

## Features

- **PDF Summarization**: Extracts key points from PDFs for quick reference.
- **Quiz Generation**: Automatically creates quizzes based on study material.
- **User-Friendly Interface**: Simple and interactive design for ease of use.
- **Free & Open-Source**: Built to help educators without any cost barriers.

## Prerequisites

Ensure you have the following installed before setting up the project:

- **Python** (Version 3.8 or higher) - [Download Python](https://www.python.org/)
- **Node.js** (Version 14.x or higher) - [Download Node.js](https://nodejs.org/)
- **npm** (Node.js package manager, installed alongside Node.js)

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/Divyanshu-Off/Te-AI.git
cd Te-AI
```

### 2. Set Up the Backend
Navigate to the backend directory and install dependencies:
```bash
cd backend
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
pip install -r requirements.txt
```

#### Required Python Libraries
The backend relies on the following Python packages:
- `fastapi` - For the backend API
- `uvicorn` - To run the FastAPI server
- `PyMuPDF` - For PDF processing
- `DeepSeek` - AI model for summarization and quiz generation
- `requests` - To handle HTTP requests
- `numpy` - Useful for AI-related operations
- `pydantic` - Data validation and settings management

These dependencies are automatically installed via:
```bash
pip install -r requirements.txt
```

### 3. Set Up the Frontend
Navigate to the frontend directory and install dependencies:
```bash
cd ../frontend
npm install
```

## Setting Up Gemini API
This project uses the **Gemini API** for AI-based summarization and quiz generation. You will need to obtain your own API key to use the functionality.

### How to Get a Gemini API Key
1. Go to [Google AI Gemini](https://ai.google.dev/)
2. Sign in with your Google account.
3. Navigate to the **API Keys** section.
4. Generate a new API key and copy it.

### Adding Your API Key
Once you have the key, create a `.env` file inside the `backend` directory and add:
```
GEMINI_API_KEY=your_api_key_here
```
Ensure that you replace `your_api_key_here` with your actual Gemini API key.

## Usage

### 1. Start the Backend Server
```bash
cd backend
source env/bin/activate  # On Windows: env\Scripts\activate
uvicorn main:app --reload
```

### 2. Start the Frontend Development Server
Open a new terminal window:
```bash
cd frontend
npm start
```

## License
This project is licensed under the GNU General Public License v3.0. See the [LICENSE](LICENSE) file for details.

## Contact
For questions or suggestions, reach out at [](divyanshuansh07@gmail.com).
