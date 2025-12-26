// MediScan Frontend Application
class MediScanApp {
    constructor() {
        this.API_BASE_URL = 'http://localhost:5000/api';
        this.initializeApp();
    }
    
    initializeApp() {
        console.log('🚀 MediScan Frontend Initialized');
        this.bindEventListeners();
        this.updateInputStats();
        this.testBackendConnection();
    }
    
    bindEventListeners() {
        // Get DOM elements
        this.medicalText = document.getElementById('medicalText');
        this.summarizeBtn = document.getElementById('summarizeBtn');
        this.clearBtn = document.getElementById('clearBtn');
        this.sampleBtn = document.getElementById('sampleBtn');
        this.retryBtn = document.getElementById('retryBtn');
        this.copySummaryBtn = document.getElementById('copySummary');
        
        // Bind events
        this.medicalText.addEventListener('input', () => {
            this.updateInputStats();
            this.toggleSummarizeButton();
        });
        
        this.summarizeBtn.addEventListener('click', () => this.summarizeReport());
        this.clearBtn.addEventListener('click', () => this.clearInput());
        this.sampleBtn.addEventListener('click', () => this.loadSampleReport());
        this.retryBtn.addEventListener('click', () => this.retryAnalysis());
        this.copySummaryBtn.addEventListener('click', () => this.copySummaryToClipboard());
        
        // Enter key shortcut
        this.medicalText.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'Enter') {
                this.summarizeReport();
            }
        });
    }
    
    updateInputStats() {
        const text = this.medicalText.value;
        const wordCount = text.trim() ? text.trim().split(/\s+/).length : 0;
        const charCount = text.length;
        
        document.getElementById('wordCount').textContent = `${wordCount} words`;
        document.getElementById('charCount').textContent = `${charCount} characters`;
    }
    
    toggleSummarizeButton() {
        const hasText = this.medicalText.value.trim().length > 0;
        this.summarizeBtn.disabled = !hasText;
    }
    
    async testBackendConnection() {
        try {
            const response = await fetch(`${this.API_BASE_URL}/health`);
            const data = await response.json();
            
            if (data.status === 'healthy') {
                console.log('✅ Backend connection successful');
                this.updateAIStatus('✅ Connected');
            } else {
                this.updateAIStatus('❌ Issues');
            }
        } catch (error) {
            console.error('❌ Backend connection failed:', error);
            this.updateAIStatus('❌ Offline');
            this.showNotification('Backend server is not running. Please start the Flask server.', 'error');
        }
    }
    
    updateAIStatus(status) {
        const aiStatusElement = document.getElementById('aiStatus');
        if (aiStatusElement) {
            aiStatusElement.textContent = status;
        }
    }
    
    async summarizeReport() {
        const text = this.medicalText.value.trim();
        
        if (!text) {
            this.showNotification('Please enter a medical report to analyze.', 'warning');
            return;
        }
        
        if (text.length < 50) {
            if (!confirm('The report seems very short. Would you like to proceed anyway?')) {
                return;
            }
        }
        
        this.showLoading();
        this.hideResults();
        this.hideError();
        
        try {
            const startTime = Date.now();
            const response = await fetch(`${this.API_BASE_URL}/summarize`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ text: text })
            });
            
            const processingTime = ((Date.now() - startTime) / 1000).toFixed(2);
            
            if (!response.ok) {
                throw new Error(`Server error: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }
            
            this.displayResults(data, processingTime);
            this.showNotification('Report analyzed successfully!', 'success');
            
        } catch (error) {
            console.error('Analysis error:', error);
            this.showError(`Failed to analyze the report: ${error.message}`);
        } finally {
            this.hideLoading();
        }
    }
    
    displayResults(data, processingTime) {
        // Update confidence score
        this.updateConfidenceScore(data.confidence_score);
        
        // Update executive summary
        document.getElementById('executiveSummary').textContent = data.summary;
        
        // Update all analysis sections
        this.updateAnalysisSection('diagnosesList', data.diagnoses, 'No diagnoses identified');
        this.updateAnalysisSection('symptomsList', data.symptoms, 'No symptoms identified');
        this.updateAnalysisSection('keyFindingsList', data.key_findings, 'No key findings identified');
        this.updateAnalysisSection('medicationsList', data.medications, 'No medications identified');
        this.updateAnalysisSection('testsList', data.tests_performed, 'No tests identified');
        this.updateAnalysisSection('recommendationsList', data.recommendations, 'No recommendations identified');
        
        // Update statistics
        document.getElementById('wordCountResult').textContent = data.word_count || 0;
        document.getElementById('processingTime').textContent = `${processingTime}s`;
        document.getElementById('findingsCount').textContent = data.key_findings?.length || 0;
        
        this.showResults();
    }
    
    updateConfidenceScore(confidence) {
        const confidenceValue = document.getElementById('confidenceValue');
        const confidenceBar = document.getElementById('confidenceBar');
        const confidenceNote = document.getElementById('confidenceNote');
        
        const percentage = Math.round(confidence * 100);
        confidenceValue.textContent = `${percentage}%`;
        
        // Set confidence bar width
        confidenceBar.style.width = `${percentage}%`;
        
        // Update color based on confidence
        if (percentage >= 70) {
            confidenceValue.style.color = '#10b981';
            confidenceNote.textContent = 'High confidence - Report contains clear medical terminology';
        } else if (percentage >= 40) {
            confidenceValue.style.color = '#f59e0b';
            confidenceNote.textContent = 'Moderate confidence - Some medical terms detected';
        } else {
            confidenceValue.style.color = '#ef4444';
            confidenceNote.textContent = 'Low confidence - Limited medical terminology found';
        }
    }
    
    updateAnalysisSection(elementId, items, emptyMessage) {
        const container = document.getElementById(elementId);
        container.innerHTML = '';
        
        if (items && items.length > 0) {
            items.forEach(item => {
                const itemElement = document.createElement('div');
                itemElement.className = 'analysis-item';
                itemElement.textContent = item;
                container.appendChild(itemElement);
            });
        } else {
            const emptyElement = document.createElement('div');
            emptyElement.className = 'empty-state';
            emptyElement.textContent = emptyMessage;
            container.appendChild(emptyElement);
        }
    }
    
    clearInput() {
        this.medicalText.value = '';
        this.updateInputStats();
        this.toggleSummarizeButton();
        this.hideResults();
        this.hideError();
        this.showNotification('Input cleared', 'info');
    }
    
    loadSampleReport() {
        const sampleReport = `
CHIEF COMPLAINT: Persistent cough and chest pain for 2 weeks.

HISTORY OF PRESENT ILLNESS: 
45-year-old male with 2-week history of productive cough, fever, 
and right-sided chest pain that worsens with deep inspiration. 
Patient reports fatigue and decreased appetite.

PHYSICAL EXAMINATION: 
- Temperature: 38.2°C
- Respiratory rate: 22 breaths/minute
- Blood pressure: 130/85 mmHg
- Decreased breath sounds on right lower lobe
- Mild tachypnea

DIAGNOSTIC STUDIES:
Chest X-ray PA and lateral views show consolidation in the right lower lobe 
consistent with pneumonia. No pleural effusion noted.

LABORATORY FINDINGS:
- White blood cell count: 15,000/μL (elevated)
- CRP: 45 mg/L (elevated)
- ESR: 65 mm/hr
- Blood cultures: Pending

ASSESSMENT/DIAGNOSIS:
1. Community-acquired pneumonia, right lower lobe
2. Moderate severity
3. Rule out complications

RECOMMENDATIONS/TREATMENT PLAN:
1. Start empiric antibiotic therapy with Levofloxacin 500mg IV daily
2. Administer antipyretics for fever management
3. Encourage pulmonary hygiene and deep breathing exercises
4. Follow up in 48 hours to assess clinical response
5. Repeat chest X-ray in 2-4 weeks to document resolution
6. Consider switching to oral therapy once afebrile for 24-48 hours

DISPOSITION:
Patient admitted for IV antibiotics and monitoring.
        `.trim();
        
        this.medicalText.value = sampleReport;
        this.updateInputStats();
        this.toggleSummarizeButton();
        this.showNotification('Sample report loaded', 'info');
        
        // Scroll to input
        this.medicalText.focus();
    }
    
    async copySummaryToClipboard() {
        const summary = document.getElementById('executiveSummary').textContent;
        try {
            await navigator.clipboard.writeText(summary);
            this.showNotification('Summary copied to clipboard!', 'success');
        } catch (err) {
            console.error('Failed to copy text: ', err);
            this.showNotification('Failed to copy summary', 'error');
        }
    }
    
    retryAnalysis() {
        this.hideError();
        this.summarizeReport();
    }
    
    showLoading() {
        document.getElementById('loading').classList.remove('hidden');
        document.querySelector('.btn-text').classList.add('hidden');
        document.querySelector('.btn-loading').classList.remove('hidden');
        this.summarizeBtn.disabled = true;
    }
    
    hideLoading() {
        document.getElementById('loading').classList.add('hidden');
        document.querySelector('.btn-text').classList.remove('hidden');
        document.querySelector('.btn-loading').classList.add('hidden');
        this.summarizeBtn.disabled = false;
    }
    
    showResults() {
        document.getElementById('results').classList.remove('hidden');
    }
    
    hideResults() {
        document.getElementById('results').classList.add('hidden');
    }
    
    showError(message) {
        document.getElementById('errorMessage').textContent = message;
        document.getElementById('error').classList.remove('hidden');
    }
    
    hideError() {
        document.getElementById('error').classList.add('hidden');
    }
    
    showNotification(message, type = 'info') {
        const notification = document.getElementById('notification');
        const notificationText = document.getElementById('notificationText');
        
        // Set background color based on type
        const colors = {
            success: '#10b981',
            error: '#ef4444',
            warning: '#f59e0b',
            info: '#3b82f6'
        };
        
        notification.style.background = colors[type] || colors.info;
        notificationText.textContent = message;
        notification.classList.remove('hidden');
        
        // Auto-hide after 3 seconds
        setTimeout(() => {
            notification.classList.add('hidden');
        }, 3000);
    }
}

// Initialize the application when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new MediScanApp();
});

// Add some utility functions to the global scope for easier debugging
window.MediScan = {
    version: '1.0.0',
    testAPI: async function() {
        try {
            const response = await fetch('http://localhost:5000/api/health');
            const data = await response.json();
            console.log('API Health:', data);
            return data;
        } catch (error) {
            console.error('API Test Failed:', error);
            return null;
        }
    }
};