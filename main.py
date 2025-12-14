#!/usr/bin/env python3
"""
Image Hash Service
Servicio para calcular el pHash de una imagen.
"""

from flask import Flask, request, jsonify
from PIL import Image
import imagehash
import io
import os
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}

def allowed_file(filename):
    """Check if the file has an allowed extension"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'}), 200

@app.route('/phash', methods=['POST'])
def calculate_phash():
    """
    Calculate perceptual hash (pHash) for an uploaded image
    """
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400
    
    file = request.files['image']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    # Validate file extension
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Allowed types: ' + ', '.join(ALLOWED_EXTENSIONS)}), 400
    
    # Check file size using content length if available
    content_length = request.content_length
    if content_length and content_length > MAX_FILE_SIZE:
        return jsonify({'error': f'File too large. Maximum size: {MAX_FILE_SIZE / (1024 * 1024)} MB'}), 400
    
    try:
        # Read image from uploaded file
        image_bytes = file.read()
        
        # Additional size check after reading
        if len(image_bytes) > MAX_FILE_SIZE:
            return jsonify({'error': f'File too large. Maximum size: {MAX_FILE_SIZE / (1024 * 1024)} MB'}), 400
        
        image = Image.open(io.BytesIO(image_bytes))
        
        # Verify it's a valid image by attempting to load it
        image.verify()
        
        # Reopen image for processing (verify() closes the file)
        image = Image.open(io.BytesIO(image_bytes))
        
        # Calculate perceptual hash
        hash_value = imagehash.phash(image)
        
        return jsonify({
            'phash': str(hash_value)
        }), 200
    
    except Exception as e:
        # Log the full error for debugging
        logger.error(f"Error processing image: {str(e)}", exc_info=True)
        # Return generic error message to client
        return jsonify({'error': 'Failed to process image'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
