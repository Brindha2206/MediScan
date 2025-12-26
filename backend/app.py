from flask import Flask, request, jsonify
from flask_cors import CORS
import config
from nlp_processor import MedicalReportProcessor
import time

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(config.Config)
CORS(app)

# Initialize the NLP processor
print("🔄 Starting MediScan NLP Engine...")
nlp_processor = MedicalReportProcessor()
print("✅ MediScan NLP Engine Ready!")

@app.route('/')
def home():
    """Home endpoint to check if API is running"""
    return jsonify({
        "message": "MediScan API is running!",
        "status": "success",
        "version": "1.0.0",
        "endpoints": {
            "health": "/api/health",
            "summarize": "/api/summarize (POST)",
            "demo": "/api/demo"
        }
    })

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "MediScan API",
        "timestamp": time.time()
    })

@app.route('/api/summarize', methods=['POST'])
def summarize_report():
    """
    Main endpoint for summarizing medical reports
    Expects JSON: {'text': 'medical report text'}
    """
    try:
        start_time = time.time()
        
        # Get JSON data from request
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'No JSON data provided',
                'message': 'Please send JSON with "text" field'
            }), 400
        
        medical_text = data.get('text', '')
        
        if not medical_text:
            return jsonify({
                'error': 'No text provided',
                'message': 'Please provide medical text in the "text" field'
            }), 400
        
        # Process the medical report
        result = nlp_processor.process_report(medical_text)
        
        # Add processing time
        result['processing_time_seconds'] = round(time.time() - start_time, 2)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@app.route('/api/demo', methods=['GET'])
def demo_endpoint():
    """Demo endpoint with sample medical report"""
    sample_report = """
    CHIEF COMPLAINT: Persistent cough and chest pain.

    HISTORY: 45-year-old male with 2-week history of productive cough, fever, 
    and right-sided chest pain that worsens with deep inspiration.

    PHYSICAL EXAM: 
    - Temperature: 38.2°C
    - Respiratory rate: 22 breaths/minute
    - Decreased breath sounds on right lower lobe

    DIAGNOSTIC STUDIES:
    Chest X-ray shows consolidation in right lower lobe consistent with pneumonia.

    LABORATORY:
    - White blood cell count: 15,000/μL (elevated)
    - CRP: 45 mg/L (elevated)

    ASSESSMENT:
    1. Community-acquired pneumonia, right lower lobe
    2. Moderate severity

    PLAN:
    1. Start empiric antibiotic therapy with Levofloxacin 500mg daily
    2. Follow up in 48 hours to assess clinical response
    3. Repeat chest X-ray in 4 weeks
    4. Symptomatic management with antipyretics
    """
    
    result = nlp_processor.process_report(sample_report)
    return jsonify({
        'demo_report': sample_report,
        'analysis': result
    })

if __name__ == '__main__':
    print("\n" + "="*50)
    print("🩺 MediScan Server Starting...")
    print("📍 API URL: http://localhost:5000")
    print("📍 Health Check: http://localhost:5000/api/health")
    print("📍 Demo: http://localhost:5000/api/demo")
    print("="*50)
    app.run(debug=True, port=5000)