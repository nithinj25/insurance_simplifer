from flask import Flask, jsonify, request
from enhanced_analyzer import extract_text_from_pdf, save_simplified_text
import os
from werkzeug.utils import secure_filename
import logging
import tempfile

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configure upload folder using tempfile for better cross-platform compatibility
UPLOAD_FOLDER = tempfile.gettempdir()
ALLOWED_EXTENSIONS = {'pdf'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

def allowed_file(filename):
    """Check if the file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_pdf(pdf_path):
    """Process the PDF file and return simplified text."""
    try:
        logger.info(f"Processing PDF: {pdf_path}")
        # Extract text from PDF
        text = extract_text_from_pdf(pdf_path)
        logger.info(f"Successfully extracted text from PDF")
        
        # Generate simplified text
        save_simplified_text(text, "simplified_text.txt")
        logger.info("Successfully generated simplified text")
        
        # Read the generated simplified text
        with open("simplified_text.txt", "r", encoding="utf-8") as f:
            content = f.read()
            
        return content
    except Exception as e:
        logger.error(f"Error processing PDF: {str(e)}")
        raise

@app.route('/api/simplify-policy', methods=['POST'])
def simplify_policy():
    """API endpoint to upload and process a policy PDF."""
    try:
        logger.info("Received request to /api/simplify-policy")
        
        # Check if file was uploaded
        if 'file' not in request.files:
            logger.error("No file in request")
            return jsonify({
                "status": "error",
                "message": "No file uploaded"
            }), 400
        
        file = request.files['file']
        
        # Check if file is empty
        if file.filename == '':
            logger.error("Empty filename")
            return jsonify({
                "status": "error",
                "message": "No file selected"
            }), 400
        
        # Check if file type is allowed
        if not allowed_file(file.filename):
            logger.error(f"Invalid file type: {file.filename}")
            return jsonify({
                "status": "error",
                "message": "File type not allowed. Only PDF files are accepted."
            }), 400
        
        # Save the uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        logger.info(f"Saving file to: {filepath}")
        
        try:
            file.save(filepath)
            logger.info("File saved successfully")
        except Exception as e:
            logger.error(f"Error saving file: {str(e)}")
            return jsonify({
                "status": "error",
                "message": f"Error saving file: {str(e)}"
            }), 500
        
        try:
            # Process the PDF
            content = process_pdf(filepath)
            
            # Clean up the uploaded file
            os.remove(filepath)
            logger.info("File processed and cleaned up successfully")
            
            return jsonify({
                "status": "success",
                "data": content
            })
            
        except Exception as e:
            # Clean up file even if processing fails
            if os.path.exists(filepath):
                os.remove(filepath)
            logger.error(f"Error processing file: {str(e)}")
            return jsonify({
                "status": "error",
                "message": f"Error processing file: {str(e)}"
            }), 500
        
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Unexpected error: {str(e)}"
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for Render."""
    return jsonify({
        "status": "healthy",
        "message": "API is running"
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"Starting server on port {port}")
    app.run(host='0.0.0.0', port=port) 