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

app = Flask(__name__)

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
    
    try:
        # Read image from uploaded file
        image_bytes = file.read()
        image = Image.open(io.BytesIO(image_bytes))
        
        # Calculate perceptual hash
        hash_value = imagehash.phash(image)
        
        return jsonify({
            'phash': str(hash_value),
            'hash_size': hash_value.hash.size
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
