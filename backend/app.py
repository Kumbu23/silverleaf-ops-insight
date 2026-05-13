from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import os
import sys
from werkzeug.utils import secure_filename
from datetime import datetime
import traceback

from config import config
from data_processor import DataProcessor
from anomaly_detector import AnomalyDetector

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(config['development'])

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Enable CORS
CORS(app)

# Initialize processors
data_processor = DataProcessor()
anomaly_detector = AnomalyDetector()


def get_project_path(*parts):
    base_dir = os.path.dirname(__file__)
    local_path = os.path.join(base_dir, *parts)
    if os.path.exists(local_path):
        return os.path.abspath(local_path)
    parent_path = os.path.join(base_dir, '..', *parts)
    if os.path.exists(parent_path):
        return os.path.abspath(parent_path)
    return local_path


@app.route('/')
def index():
    """Serve the dashboard."""
    frontend_path = get_project_path('frontend', 'index.html')
    with open(frontend_path, 'r') as f:
        return f.read()

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Upload and process fee CSV file."""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not file.filename.endswith('.csv'):
            return jsonify({'error': 'File must be CSV format'}), 400
        
        # Save file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Process CSV
        df = data_processor.load_csv(filepath)
        report = data_processor.generate_report(df)
        
        return jsonify(report), 200
    
    except Exception as e:
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

@app.route('/api/sample', methods=['GET'])
def get_sample_report():
    """Return report with sample data."""
    try:
        sample_path = get_project_path('sample_data', 'fee_records.csv')
        if not os.path.exists(sample_path):
            return jsonify({'error': 'Sample data not found'}), 404
        
        df = data_processor.load_csv(sample_path)
        report = data_processor.generate_report(df)
        
        return jsonify(report), 200
    
    except Exception as e:
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
