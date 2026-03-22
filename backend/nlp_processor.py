import spacy
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize
import re

class MedicalReportProcessor:
    def __init__(self):
        print("Loading Medical NLP Processor...")
        
        # Load spaCy model
        try:
            self.nlp = spacy.load("en_core_web_sm")
            print("spaCy model loaded successfully")
        except OSError:
            print("Downloading spaCy model...")
            import os
            os.system("python -m spacy download en_core_web_sm")
            self.nlp = spacy.load("en_core_web_sm")
            print("spaCy model downloaded and loaded")
        
        # Prepare only the NLTK resources we actually use.
        print("Preparing NLTK resources...")
        self._ensure_nltk_resource('corpora/stopwords', 'stopwords')
        print("NLTK resources ready")
        
        # Medical terminology database
        self.medical_terms = self._initialize_medical_terms()
        self.stop_words = set(stopwords.words('english')) if self._ensure_nltk_resource('corpora/stopwords', 'stopwords') else set()
        
        print("Medical NLP Processor ready!")

    def _ensure_nltk_resource(self, resource_path, resource_name):
        """Best-effort NLTK data loader."""
        try:
            nltk.data.find(resource_path)
            return True
        except LookupError:
            try:
                nltk.download(resource_name, quiet=True)
                nltk.data.find(resource_path)
                return True
            except LookupError:
                return False

    def _safe_sent_tokenize(self, text):
        """Use NLTK when available, otherwise fall back to regex splitting."""
        try:
            return [sentence.strip() for sentence in sent_tokenize(text) if sentence.strip()]
        except LookupError:
            return [
                sentence.strip()
                for sentence in re.split(r'(?<=[.!?])\s+|\n+', text)
                if sentence.strip()
            ]
    
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
                'infection', 'inflammation', 'fracture', 'bleeding', 'opacity',
                'effusion', 'consolidation', 'nodule', 'thickening'
            ],
            'section_headers': [
                'diagnosis', 'diagnoses', 'assessment', 'impression', 'conclusion',
                'final diagnosis', 'recommendation', 'recommendations', 'plan',
                'treatment plan', 'findings', 'laboratory findings', 'laboratory',
                'diagnostic studies', 'chief complaint', 'symptoms', 'history',
                'history of present illness', 'physical examination', 'disposition'
            ]
        }

    def _split_lines(self, text):
        return [line.strip() for line in text.splitlines() if line.strip()]

    def _normalize_header_variants(self, value):
        normalized = value.lower().strip().strip(':')
        variants = {
            normalized,
            normalized.replace('/', ' '),
            normalized.replace('/', ''),
            normalized.replace('&', ' '),
        }

        for separator in ['/', '&']:
            if separator in normalized:
                for part in normalized.split(separator):
                    cleaned = part.strip()
                    if cleaned:
                        variants.add(cleaned)

        return {variant for variant in variants if variant}

    def _unique_preserve_order(self, items, max_items=None):
        results = []
        seen = set()
        for item in items:
            normalized = re.sub(r'\s+', ' ', item).strip(" .;:-")
            if not normalized:
                continue
            key = normalized.lower()
            if key in seen:
                continue
            seen.add(key)
            results.append(normalized)
            if max_items and len(results) >= max_items:
                break
        return results

    def _split_section_value(self, value):
        cleaned = re.sub(r'^\d+[\.\)]\s*', '', value).strip()
        if not cleaned:
            return []

        parts = re.split(r';|\s+\d+[\.\)]\s+', cleaned)
        return [part.strip(" -") for part in parts if len(part.strip()) > 2]

    def _extract_section_items(self, text, headers):
        lines = self._split_lines(text)
        target_headers = {header.lower() for header in headers}
        known_sections = {header.lower() for header in self.medical_terms['section_headers']}
        items = []

        for index, line in enumerate(lines):
            line_lower = line.lower().rstrip(':')
            line_variants = self._normalize_header_variants(line_lower)

            if not (line_variants & target_headers):
                continue

            inline_value = line.split(':', 1)[1].strip() if ':' in line else ""
            if inline_value:
                items.extend(self._split_section_value(inline_value))

            next_index = index + 1
            while next_index < len(lines):
                next_line = lines[next_index]
                next_lower = next_line.lower().rstrip(':')
                next_variants = self._normalize_header_variants(next_lower)
                if next_variants & known_sections:
                    break
                items.extend(self._split_section_value(next_line))
                next_index += 1

        return self._unique_preserve_order(items)
    
    def process_report(self, text):
        """
        Main method to process medical report and generate summary
        """
        print(f"Processing medical report ({len(text)} characters)...")
        
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
            
            print(f"Report processed successfully. Confidence: {confidence}")
            return response
            
        except Exception as e:
            print(f"Error processing report: {str(e)}")
            return self._get_error_response(str(e))
    
    def _clean_text(self, text):
        """Clean and normalize medical text"""
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        text = re.sub(r'[ \t]+', ' ', text)
        text = re.sub(r'\n\s*\n+', '\n', text)
        text = re.sub(r'[^\w\s\.\,\-\%\(\)\:\;\/\+]', '', text)
        return text.strip()
    
    def _extract_key_findings(self, text):
        """Extract important medical findings"""
        findings = []

        findings.extend(self._extract_section_items(
            text,
            ['findings', 'laboratory findings', 'laboratory', 'impression', 'conclusion']
        ))

        sentences = self._safe_sent_tokenize(text)
        for sentence in sentences:
            sentence_lower = sentence.lower()
            
            # Check for critical finding indicators
            if any(keyword in sentence_lower for keyword in self.medical_terms['critical_findings']):
                # Check if it's actually a finding (not a normal finding)
                if 'normal' not in sentence_lower and 'unremarkable' not in sentence_lower:
                    findings.append(sentence.strip())
            
            # Look for numerical findings (lab values, measurements)
            if re.search(r'\d+\.?\d*\s*(mg/dl|mg/l|g/dl|mm|cm|kg|%|mmhg|/ul|mm/hr)', sentence, re.IGNORECASE):
                findings.append(sentence.strip())

        return self._unique_preserve_order(findings, max_items=8)
    
    def _extract_diagnoses(self, text):
        """Extract diagnosis information"""
        diagnoses = []

        diagnoses.extend(self._extract_section_items(
            text,
            ['diagnosis', 'diagnoses', 'assessment', 'final diagnosis', 'impression', 'conclusion']
        ))

        patterns = [
            r'(?im)^\s*diagnosis\s*:\s*([^\.\n]+)',
            r'(?im)^\s*impression\s*:\s*([^\.\n]+)',
            r'(?im)^\s*final diagnosis\s*:\s*([^\.\n]+)',
            r'(?im)^\s*diagnosed with\s*:?\s*([^\.\n]+)',
            r'(?im)^\s*condition\s*:\s*([^\.\n]+)',
            r'(?im)^\s*assessment\s*:\s*([^\.\n]+)',
            r'(?im)^\s*conclusion\s*:\s*([^\.\n]+)'
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                diagnosis = match.group(1).strip()
                if len(diagnosis) > 5:  # Avoid very short matches
                    diagnoses.append(diagnosis)
        
        diagnoses = [
            diagnosis for diagnosis in diagnoses
            if not diagnosis.startswith('/')
            and 'rule out' not in diagnosis.lower()
            and 'possible' not in diagnosis.lower()
            and 'suspected' not in diagnosis.lower()
        ]

        return self._unique_preserve_order(diagnoses, max_items=5)
    
    def _extract_medications(self, text):
        """Extract medication information"""
        medications = []
        
        # Look for medication patterns
        patterns = [
            r'([A-Z][a-zA-Z]+(?:\s+[A-Z]?[a-zA-Z]+)?\s+\d+\s*(?:mg|mcg|g|ml))',
            r'prescribed\s+([^\.]+)',
            r'medication:?\s*([^\.]+)',
            r'taking\s+([^\.]+)',
            r'start\s+([^\.]+)',
            r'continue\s+([^\.]+)',
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                med = match.group(1).strip()
                if len(med) > 3:
                    medications.append(med)
        
        return self._unique_preserve_order(medications, max_items=5)
    
    def _extract_tests(self, text):
        """Extract medical tests mentioned"""
        tests = []

        tests.extend(self._extract_section_items(
            text,
            ['diagnostic studies', 'laboratory findings', 'laboratory', 'tests']
        ))

        sentences = self._safe_sent_tokenize(text)
        for sentence in sentences:
            sentence_lower = sentence.lower()
            if any(test in sentence_lower for test in self.medical_terms['test_keywords']):
                tests.append(sentence.strip())

        return self._unique_preserve_order(tests, max_items=5)
    
    def _extract_symptoms(self, text):
        """Extract patient symptoms"""
        symptoms = []

        symptoms.extend(self._extract_section_items(
            text,
            ['chief complaint', 'symptoms']
        ))

        symptom_patterns = [
            r'complains of\s+([^\.]+)',
            r'reports\s+([^\.]+)',
            r'presents with\s+([^\.]+)',
            r'symptoms:?\s*([^\.\n]+)',
            r'chief complaint:?\s*([^\.\n]+)'
        ]
        
        for pattern in symptom_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                symptom_text = match.group(1).strip()
                symptoms.extend([s.strip() for s in symptom_text.split(',')])
        
        return self._unique_preserve_order(symptoms, max_items=8)
    
    def _extract_recommendations(self, text):
        """Extract recommendations and next steps"""
        recommendations = []

        recommendations.extend(self._extract_section_items(
            text,
            ['recommendation', 'recommendations', 'plan', 'treatment plan']
        ))

        sentences = self._safe_sent_tokenize(text)
        for sentence in sentences:
            sentence_lower = sentence.lower()
            stripped = sentence.strip(" :-").lower()

            if stripped in self.medical_terms['section_headers']:
                continue
            
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
        
        recommendations = [
            item for item in recommendations
            if 'rule out' not in item.lower()
        ]

        return self._unique_preserve_order(recommendations, max_items=5)
    
    def _generate_comprehensive_summary(self, diagnoses, findings, recommendations, symptoms):
        """Generate a patient-friendly summary"""
        summary_parts = []
        
        # Diagnosis section
        if diagnoses:
            if len(diagnoses) == 1:
                summary_parts.append(f"Diagnosis: {diagnoses[0]}")
            else:
                summary_parts.append(f"Primary Diagnoses: {', '.join(diagnoses[:2])}")
        
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
        
        if not summary_parts:
            summary_parts.append("No specific diagnosis mentioned in the report.")

        return " | ".join(summary_parts)
    
    def _calculate_confidence_score(self, text):
        """Estimate confidence based on report richness and structure."""
        text_lower = text.lower()
        word_count = len(text.split())

        if word_count < 12:
            return 0.18

        medical_term_count = 0
        for category_name, category_terms in self.medical_terms.items():
            if category_name == 'section_headers':
                continue
            for term in category_terms:
                if term in text_lower:
                    medical_term_count += 1

        section_count = sum(1 for header in self.medical_terms['section_headers'] if header in text_lower)
        numeric_finding_count = len(re.findall(r'\d+\.?\d*\s*(mg/dl|mg/l|g/dl|mm|cm|kg|%|mmhg|/ul|mm/hr|bpm)', text, re.IGNORECASE))

        confidence = 0.12
        confidence += min(word_count / 250, 0.24)
        confidence += min(medical_term_count / 18, 0.24)
        confidence += min(section_count / 8, 0.18)
        confidence += min(numeric_finding_count / 5, 0.12)

        if any(keyword in text_lower for keyword in ['assessment', 'diagnosis', 'impression', 'conclusion']):
            confidence += 0.08
        if any(keyword in text_lower for keyword in ['plan', 'recommendation', 'treatment plan']):
            confidence += 0.05
        if any(keyword in text_lower for keyword in ['x-ray', 'mri', 'ct', 'ultrasound', 'laboratory', 'crp', 'wbc']):
            confidence += 0.05

        confidence = min(confidence, 0.93)
        return round(max(confidence, 0.18), 2)
    
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
