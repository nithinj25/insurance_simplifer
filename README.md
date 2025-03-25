# Policy Document Simplifier API

A Flask API that simplifies insurance policy documents by extracting and organizing key information.

## Features

- PDF document processing
- Text extraction and analysis
- Structured output of policy information
- RESTful API endpoints

## API Endpoints

### POST /api/simplify-policy
Upload and process a policy PDF document.

**Request:**
- Method: POST
- Content-Type: multipart/form-data
- Body: 
  - file: PDF file to process

**Response:**
```json
{
    "status": "success",
    "data": "simplified text content"
}
```

### GET /health
Health check endpoint.

**Response:**
```json
{
    "status": "healthy",
    "message": "API is running"
}
```

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd policy-doc-simplifier
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python app.py
```

## Dependencies

- Flask
- PyPDF2
- gunicorn
- Werkzeug

## License

MIT License 