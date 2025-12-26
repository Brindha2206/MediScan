import spacy
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
import re
from collections import Counter
import string

class MedicalReportProcessor:
    def __init__(self):
        print("🔄 Loading Medical NLP Processor...")
        
        # Load spaCy model
        try:
            self.nlp = spacy.load("en_core_web_sm")
            print("✅ spaCy model loaded successfully")
        except OSError:
            print("📥 Downloading spaCy model...")
            import os
            os.system("python -m spacy download en_core_web_sm")
            self.nlp = spacy.load("en_core_web_sm")
            print("✅ spaCy model downloaded and loaded")
        
        # Download NLTK resources
        print("📥 Downloading NLTK resources...")
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
        nltk.download('averaged_perceptron_tagger', quiet=True)
        print("✅ NLTK resources downloaded")
        
        # Medical terminology database
        self.medical_terms = self._initialize_medical_terms()
        self.stop_words = set(stopwords.words('english'))
        
        print("✅ Medical NLP Processor ready!")
    
    def _initialize_medical_terms(self):
        """Comprehensive medical terminology database"""
        return {
            'diagnosis_keywords': [
                'diagnosis', 'diagnosed', 'impression', 'finding', 'findings',
                'condition', 'disorder', 'disease', 'syndrome', 'diagnoses'
            ],
            'symptom_keywords': [
                'symptom', 'symptoms', 'complaint', 'presents with', 'experienced',
                'pain', 'fever', 'cough', 'headache', 'nausea', 'vomiting', 'fatigue',
                'weakness', 'shortness of breath', 'chest pain', 'abdominal pain'
            ],
            'medication_keywords': [
                'medication', 'medications', 'prescription', 'drug', 'therapy',
                'treatment', 'dose', 'dosage', 'mg', 'tablet', 'injection',
                'antibiotic', 'analgesic', 'antihypertensive'
            ],
            'test_keywords': [
                'test', 'tests', 'laboratory', 'lab', 'scan', 'x-ray', 'xray',
                'mri', 'ct', 'ultrasound', 'blood test', 'urine test', 'biopsy',
                'culture', 'imaging', 'procedure'
            ],
            'recommendation_keywords': [
                'recommend', 'recommendation', 'recommended', 'advise', 'advice',
                'suggest', 'suggestion', 'should', 'must', 'follow up', 'follow-up',
                'next steps', 'plan', 'management', 'treatment plan'
            ],
            'critical_findings': [
                'abnormal', 'elevated', 'decreased', 'increased', 'positive',
                'negative', 'normal', 'abnormality', 'mass', 'lesion', 'tumor',
                'infection', 'inflammation', 'fracture', 'bleeding'
            ]
        }
    
    def process_report(self, text):
        """
        Main method to process medical report and generate summary
        """
        print(f"📄 Processing medical report ({len(text)} characters)...")
        
        if not text or len(text.strip()) < 10:
            return self._get_empty_response()
        
        try:
            # Step 1: Clean and preprocess text
            cleaned_text = self._clean_text(text)
            
            # Step 2: Extract key components
            key_findings = self._extract_key_findings(cleaned_text)
            diagnoses = self._extract_diagnoses(cleaned_text)
            medications = self._extract_medications(cleaned_text)
            tests = self._extract_tests(cleaned_text)
            recommendations = self._extract_recommendations(cleaned_text)
            symptoms = self._extract_symptoms(cleaned_text)
            
            # Step 3: Generate comprehensive summary
            summary = self._generate_comprehensive_summary(
                diagnoses, key_findings, recommendations, symptoms
            )
            
            # Step 4: Calculate confidence score
            confidence = self._calculate_confidence_score(cleaned_text)
            
            response = {
                'summary': summary,
                'key_findings': key_findings,
                'diagnoses': diagnoses,
                'medications': medications,
                'tests_performed': tests,
                'symptoms': symptoms,
                'recommendations': recommendations,
                'confidence_score': confidence,
                'word_count': len(cleaned_text.split()),
                'processing_time': 'instant'
            }
            
            print(f"✅ Report processed successfully. Confidence: {confidence}")
            return response
            
        except Exception as e:
            print(f"❌ Error processing report: {str(e)}")
            return self._get_error_response(str(e))
    
    def _clean_text(self, text):
        """Clean and normalize medical text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep medical abbreviations and punctuation
        text = re.sub(r'[^\w\s\.\,\-\%\(\)\:\;]', '', text)
        # Normalize case for processing (but keep original for display)
        return text.strip()
    
    def _extract_key_findings(self, text):
        """Extract important medical findings"""
        findings = []
        
        # Use spaCy for entity recognition
        doc = self.nlp(text)
        
        # Extract medical entities
        for ent in doc.ents:
            if ent.label_ in ["DISEASE", "CONDITION", "SYMPTOM", "BODY_PART"]:
                findings.append(ent.text)
        
        # Extract sentences with critical findings
        sentences = sent_tokenize(text)
        for sentence in sentences:
            sentence_lower = sentence.lower()
            
            # Check for critical finding indicators
            if any(keyword in sentence_lower for keyword in self.medical_terms['critical_findings']):
                # Check if it's actually a finding (not a normal finding)
                if 'normal' not in sentence_lower and 'unremarkable' not in sentence_lower:
                    findings.append(sentence.strip())
            
            # Look for numerical findings (lab values, measurements)
            if re.search(r'\d+\.?\d*\s*(mg/dl|mm|cm|kg|%)', sentence, re.IGNORECASE):
                findings.append(sentence.strip())
        
        return list(set(findings))[:8]  # Return unique findings, max 8
    
    def _extract_diagnoses(self, text):
        """Extract diagnosis information"""
        diagnoses = []
        
        # Pattern matching for common diagnosis formats
        patterns = [
            r'diagnosis:?\s*([^\.\n]+)',
            r'impression:?\s*([^\.\n]+)',
            r'final diagnosis:?\s*([^\.\n]+)',
            r'diagnosed with:?\s*([^\.\n]+)',
            r'condition:?\s*([^\.\n]+)'
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                diagnosis = match.group(1).strip()
                if len(diagnosis) > 5:  # Avoid very short matches
                    diagnoses.append(diagnosis)
        
        # Use spaCy to find disease entities
        doc = self.nlp(text)
        for ent in doc.ents:
            if ent.label_ == "DISEASE":
                diagnoses.append(ent.text)
        
        return list(set(diagnoses))[:5]  # Return unique diagnoses, max 5
    
    def _extract_medications(self, text):
        """Extract medication information"""
        medications = []
        
        # Look for medication patterns
        patterns = [
            r'(\w+\s*\d+\s*mg)',
            r'prescribed\s+([^\.]+)',
            r'medication:?\s*([^\.]+)',
            r'taking\s+([^\.]+)',
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                med = match.group(1).strip()
                if len(med) > 3:
                    medications.append(med)
        
        return list(set(medications))[:5]
    
    def _extract_tests(self, text):
        """Extract medical tests mentioned"""
        tests = []
        
        # Look for test mentions
        sentences = sent_tokenize(text)
        for sentence in sentences:
            sentence_lower = sentence.lower()
            if any(test in sentence_lower for test in self.medical_terms['test_keywords']):
                tests.append(sentence.strip())
        
        return tests[:5]
    
    def _extract_symptoms(self, text):
        """Extract patient symptoms"""
        symptoms = []
        
        # Use spaCy to find symptoms
        doc = self.nlp(text)
        for ent in doc.ents:
            if ent.label_ == "SYMPTOM":
                symptoms.append(ent.text)
        
        # Pattern matching for common symptom descriptions
        symptom_patterns = [
            r'complains of\s+([^\.]+)',
            r'reports\s+([^\.]+)',
            r'presents with\s+([^\.]+)',
            r'symptoms:?\s*([^\.]+)'
        ]
        
        for pattern in symptom_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                symptom_text = match.group(1).strip()
                symptoms.extend([s.strip() for s in symptom_text.split(',')])
        
        return list(set(symptoms))[:8]
    
    def _extract_recommendations(self, text):
        """Extract recommendations and next steps"""
        recommendations = []
        
        sentences = sent_tokenize(text)
        for sentence in sentences:
            sentence_lower = sentence.lower()
            
            # Check for recommendation indicators
            if any(keyword in sentence_lower for keyword in self.medical_terms['recommendation_keywords']):
                recommendations.append(sentence.strip())
            
            # Look for follow-up instructions
            if 'follow' in sentence_lower and 'up' in sentence_lower:
                recommendations.append(sentence.strip())
            
            # Look for medication instructions
            if any(word in sentence_lower for word in ['take', 'continue', 'start', 'stop']):
                if any(med_word in sentence_lower for med_word in ['medication', 'drug', 'pill', 'tablet']):
                    recommendations.append(sentence.strip())
        
        return recommendations[:5]
    
    def _generate_comprehensive_summary(self, diagnoses, findings, recommendations, symptoms):
        """Generate a patient-friendly summary"""
        summary_parts = []
        
        # Diagnosis section
        if diagnoses:
            if len(diagnoses) == 1:
                summary_parts.append(f"Diagnosis: {diagnoses[0]}")
            else:
                summary_parts.append(f"Primary Diagnoses: {', '.join(diagnoses[:2])}")
        else:
            summary_parts.append("No specific diagnosis mentioned in the report.")
        
        # Symptoms section
        if symptoms:
            summary_parts.append(f"Key Symptoms: {', '.join(symptoms[:3])}")
        
        # Findings section
        if findings:
            summary_parts.append(f"Important Findings: {findings[0]}")
            if len(findings) > 1:
                summary_parts.append(f"Additional finding: {findings[1]}")
        
        # Recommendations section
        if recommendations:
            summary_parts.append(f"Recommendation: {recommendations[0]}")
        
        # If no specific information found
        if not summary_parts:
            summary_parts.append("The report contains general medical information. Please consult with your healthcare provider for detailed explanation.")
        
        return " | ".join(summary_parts)
    
    def _calculate_confidence_score(self, text):
        """Calculate how confident we are in the analysis"""
        word_count = len(text.split())
        if word_count < 50:
            return 0.3
        
        # Count medical terms found
        medical_term_count = 0
        text_lower = text.lower()
        
        for category in self.medical_terms.values():
            for term in category:
                if term in text_lower:
                    medical_term_count += 1
        
        # Calculate confidence based on medical term density
        term_density = medical_term_count / (word_count / 100)  # terms per 100 words
        confidence = min(term_density / 20, 0.95)  # Normalize to 0-0.95
        
        # Boost confidence for longer, more detailed reports
        if word_count > 200:
            confidence = min(confidence + 0.1, 0.95)
        
        return round(max(confidence, 0.1), 2)  # Minimum 10% confidence
    
    def _get_empty_response(self):
        """Return response for empty text"""
        return {
            'summary': 'Please provide a medical report to analyze.',
            'key_findings': [],
            'diagnoses': [],
            'medications': [],
            'tests_performed': [],
            'symptoms': [],
            'recommendations': [],
            'confidence_score': 0.0,
            'word_count': 0,
            'processing_time': 'instant'
        }
    
    def _get_error_response(self, error_msg):
        """Return response for processing errors"""
        return {
            'summary': f'Error processing report: {error_msg}',
            'key_findings': [],
            'diagnoses': [],
            'medications': [],
            'tests_performed': [],
            'symptoms': [],
            'recommendations': [],
            'confidence_score': 0.0,
            'word_count': 0,
            'processing_time': 'instant'
        }


# Test the processor
if __name__ == "__main__":
    # Test with sample medical report
    processor = MedicalReportProcessor()
    
    sample_report = """
    Patient presents with persistent cough and chest pain for 2 weeks.
    Physical examination shows decreased breath sounds on right lower lobe.
    Chest X-ray reveals consolidation consistent with pneumonia.
    Diagnosis: Community-acquired pneumonia.
    Recommendations: Start antibiotic therapy with Levofloxacin 500mg daily.
    Follow up in 48 hours to assess response.
    """
    
    result = processor.process_report(sample_report)
    print("\n" + "="*50)
    print("TEST RESULTS:")
    print("="*50)
    print(f"Summary: {result['summary']}")
    print(f"Diagnoses: {result['diagnoses']}")
    print(f"Confidence: {result['confidence_score']}")
    print("="*50)