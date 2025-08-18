import React, { useState, useEffect } from 'react';
import Header from './Header';
import LoadingSpinner from '../components/LoadingSpinner';
import AIProgressBar from '../components/AIProgressBar';
import { showToast } from '../components/CustomToast';
import { Brain, User, Activity, FileText, RefreshCw, Plus, AlertCircle, ThumbsUp, ThumbsDown, Info } from 'lucide-react';
import { aiService } from '../services/aiService';
import { useAuth } from '../context/AuthContext';
import '../assets/styles/AIAssistant.css';

const AIAssistant = () => {
  const [symptoms, setSymptoms] = useState('');
  const [patientAge, setPatientAge] = useState('');
  const [patientGender, setPatientGender] = useState('');
  const [diagnosis, setDiagnosis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [progress, setProgress] = useState(0);
  const [progressStatus, setProgressStatus] = useState('');
  const [aiStatus, setAiStatus] = useState('checking');
  const [modelInfo, setModelInfo] = useState(null);
  const [feedbackSubmitted, setFeedbackSubmitted] = useState(false);
  const { user } = useAuth();

  useEffect(() => {
    checkAiStatus();
    loadModelInfo();
  }, []);

  const checkAiStatus = async () => {
    const healthCheck = await aiService.healthCheck();
    setAiStatus(healthCheck.status);
    if (!healthCheck.success) {
      console.warn('AI service unavailable:', healthCheck.error);
    }
  };

  const loadModelInfo = async () => {
    const result = await aiService.getModelInfo();
    if (result.success) {
      setModelInfo(result.data);
    }
  };

  // Network-aware delay calculation
  const calculateDelay = () => {
    // Simulate network speed detection
    const connection = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
    let baseDelay = 3000; // Minimum 3 seconds
    
    if (connection) {
      if (connection.effectiveType === '2g') {
        baseDelay += 4000; // Slow network
      } else if (connection.effectiveType === '3g') {
        baseDelay += 2000; // Medium network
      } else if (connection.effectiveType === '4g') {
        baseDelay += 1000; // Fast network
      }
    }
    
    return Math.max(baseDelay, 3000); // Ensure minimum 3 seconds
  };

  // Progress simulation with network-aware delay
  const simulateProgress = async () => {
    const totalDelay = calculateDelay();
    const steps = 100;
    const interval = totalDelay / steps;
    
    setProgress(0);
    setProgressStatus('Initializing AI analysis...');
    
    for (let i = 0; i <= steps; i++) {
      await new Promise(resolve => setTimeout(resolve, interval));
      
      setProgress(i);
      
      if (i < 25) {
        setProgressStatus('Analyzing patient symptoms...');
      } else if (i < 50) {
        setProgressStatus('Processing medical data...');
      } else if (i < 75) {
        setProgressStatus('Generating diagnosis...');
      } else if (i < 100) {
        setProgressStatus('Finalizing prescription...');
      } else {
        setProgressStatus('Complete!');
      }
    }
  };

  const handleDiagnosis = async () => {
    if (!symptoms.trim()) {
      showToast.error('Please enter symptoms');
      return;
    }

    if (!patientAge || !patientGender) {
      showToast.error('Please enter patient age and gender');
      return;
    }

    setLoading(true);
    setError(null);
    setDiagnosis(null);
    setProgress(0);
    setFeedbackSubmitted(false);
    
    // Start progress simulation
    await simulateProgress();

    try {
      const diagnosisRequest = {
        symptoms: symptoms.trim(),
        patient_data: {
          age: parseInt(patientAge),
          gender: patientGender,
          patient_id: `temp_${Date.now()}`,
          name: 'Patient'
        },
        doctor_id: user?.id || 'doctor_001',
        include_recommendations: true,
        detailed_analysis: true
      };

      console.log('Sending diagnosis request:', diagnosisRequest);
      
      const result = await aiService.getDiagnosis(diagnosisRequest);
      
      if (result.success) {
        setDiagnosis(result.data);
        showToast.success('AI diagnosis completed successfully');
      } else {
        throw new Error(result.error || 'Failed to get diagnosis');
      }
      
    } catch (err) {
      console.error('Diagnosis error:', err);
      setError(err.message);
      
      // Show enhanced fallback with AI service status
      if (aiStatus === 'disconnected') {
        showToast.error('AI service is unavailable. Please ensure the AI diagnosis server is running on port 5001.');
        return; // Don't show mock data if AI service is down
      } else {
        showToast.error('Failed to get AI diagnosis: ' + err.message);
      }
    } finally {
      setLoading(false);
      setTimeout(() => {
        setProgress(0);
        setProgressStatus('');
      }, 1000);
    }
  };

  const handleFeedback = async (isCorrect, additionalFeedback = '') => {
    if (!diagnosis) return;
    
    try {
      const feedbackData = {
        session_id: diagnosis.session_id || `session_${Date.now()}`,
        actual_diagnosis: isCorrect ? diagnosis.diagnosis : 'Incorrect diagnosis',
        doctor_notes: additionalFeedback || '',
        treatment_outcome: isCorrect ? 'Successful' : 'Requires revision',
        doctor_id: user?.id || 'doctor_001',
        timestamp: new Date().toISOString()
      };

      const result = await aiService.provideFeedback(feedbackData);
      
      if (result.success) {
        setFeedbackSubmitted(true);
        showToast.success('Thank you! Your feedback helps improve our AI model.');
      } else {
        showToast.error('Failed to submit feedback: ' + result.error);
      }
    } catch (error) {
      console.error('Feedback error:', error);
      showToast.error('Failed to submit feedback');
    }
  };

  const handleClear = () => {
    setSymptoms('');
    setPatientAge('');
    setPatientGender('');
    setDiagnosis(null);
    setError(null);
    setProgress(0);
    setProgressStatus('');
    setFeedbackSubmitted(false);
    showToast.info('Form cleared');
  };

  return (
    <div className="ai-assistant-container">
      {/* Background crosses */}
      <div className="background-crosses">
        {[...Array(12)].map((_, i) => (
          <span key={i} className={`cross cross-${i + 1}`}>
            <Plus size={24} />
          </span>
        ))}
      </div>

      <Header />
      
      <main className="ai-main-content">
        <div className="max-w-7xl mx-auto px-4 py-8">
          {/* Header Section */}
          <div className="ai-header">
            <div className="ai-header-icon">
              <Brain className="w-8 h-8 text-white" />
            </div>
            <h1>AI Assistant</h1>
            <p>
              AI-Driven Diagnosis and Prescription System with Blockchain-Integrated Health Records
            </p>
            
            {/* AI Status Indicator */}
            <div className="flex items-center justify-center mt-4 space-x-4">
              <div className={`flex items-center px-3 py-1 rounded-full text-sm ${
                aiStatus === 'connected' ? 'bg-green-100 text-green-800' :
                aiStatus === 'disconnected' ? 'bg-red-100 text-red-800' :
                'bg-yellow-100 text-yellow-800'
              }`}>
                <div className={`w-2 h-2 rounded-full mr-2 ${
                  aiStatus === 'connected' ? 'bg-green-500' :
                  aiStatus === 'disconnected' ? 'bg-red-500' :
                  'bg-yellow-500'
                }`}></div>
                AI Service: {aiStatus === 'connected' ? 'Connected' : 
                           aiStatus === 'disconnected' ? 'Disconnected' : 'Checking...'}
              </div>
              
              {modelInfo && (
                <div className="text-sm text-gray-600">
                  Model: {modelInfo.version} | Accuracy: {modelInfo.accuracy}%
                </div>
              )}
            </div>
          </div>

          <div className="ai-grid">
            {/* Input Section */}
            <div className="ai-card">
              <div className="ai-card-header">
                <Activity className="w-6 h-6 mr-2 text-blue-600" />
                Patient Symptoms
              </div>

              <div className="space-y-6">
                {/* Patient Age */}
                <div className="ai-form-group">
                  <label className="ai-label">
                    <User className="w-4 h-4 inline mr-1" />
                    Patient Age
                  </label>
                  <input
                    type="number"
                    value={patientAge}
                    onChange={(e) => setPatientAge(e.target.value)}
                    placeholder="Enter patient age (e.g., 35)"
                    min="1"
                    max="120"
                    className="ai-select"
                  />
                </div>

                {/* Patient Gender */}
                <div className="ai-form-group">
                  <label className="ai-label">
                    <User className="w-4 h-4 inline mr-1" />
                    Patient Gender
                  </label>
                  <select
                    value={patientGender}
                    onChange={(e) => setPatientGender(e.target.value)}
                    className="ai-select"
                  >
                    <option value="">Select gender...</option>
                    <option value="Male">Male</option>
                    <option value="Female">Female</option>
                    <option value="Other">Other</option>
                  </select>
                </div>

                {/* Symptoms Input */}
                <div className="ai-form-group">
                  <label className="ai-label">
                    <FileText className="w-4 h-4 inline mr-1" />
                    Describe Symptoms
                  </label>
                  <textarea
                    value={symptoms}
                    onChange={(e) => setSymptoms(e.target.value)}
                    placeholder="Enter patient symptoms (e.g., fever, cough, headache, fatigue...)"
                    rows={6}
                    className="ai-textarea"
                  />
                </div>

                {/* Action Buttons */}
                <div className="ai-button-group">
                  <button
                    onClick={handleDiagnosis}
                    disabled={loading || !patientAge || !patientGender || !symptoms.trim()}
                    className="ai-primary-button"
                  >
                    {loading ? 'Processing...' : (
                      <>
                        <Brain className="w-5 h-5 mr-2" />
                        Run AI Diagnosis
                      </>
                    )}
                  </button>
                  <button
                    onClick={handleClear}
                    disabled={loading}
                    className="ai-secondary-button"
                  >
                    <RefreshCw className="w-5 h-5 mr-2" />
                    Clear
                  </button>
                </div>
              </div>
            </div>

            {/* Output Section */}
            <div className="ai-card">
              <div className="ai-card-header">
                <FileText className="w-6 h-6 mr-2 text-green-600" />
                AI Diagnosis & Prescription
              </div>

              {loading && (
                <div className="ai-loading-container">
                  <AIProgressBar 
                    isLoading={loading} 
                    progress={progress} 
                    status={progressStatus} 
                  />
                </div>
              )}

              {error && (
                <div className="ai-output-card red">
                  <div className="flex items-center">
                    <AlertCircle className="w-5 h-5 mr-2" />
                    <p className="ai-output-content">{error}</p>
                  </div>
                </div>
              )}

              {diagnosis && !loading && (
                <div className="space-y-6">
                  {/* Patient Info */}
                  <div className="ai-output-card gray">
                    <h3 className="ai-output-title">Patient Information</h3>
                    <p className="ai-output-content">
                      Age: {patientAge} years, Gender: {patientGender}
                    </p>
                    <p className="text-sm text-gray-600">
                      Symptoms: {symptoms}
                    </p>
                  </div>

                  {/* Diagnosis */}
                  <div className="ai-output-card blue">
                    <h3 className="ai-output-title">AI Diagnosis</h3>
                    <p className="ai-output-content">{diagnosis.diagnosis}</p>
                    <div className="mt-2 flex items-center justify-between">
                      <span className="text-sm">
                        Confidence: {Math.round((diagnosis.confidence || 0) * 100)}%
                      </span>
                      {diagnosis.severity && (
                        <span className={`px-2 py-1 rounded text-xs font-medium ${
                          diagnosis.severity === 'Critical' ? 'bg-red-100 text-red-800' :
                          diagnosis.severity === 'Moderate' ? 'bg-orange-100 text-orange-800' :
                          'bg-green-100 text-green-800'
                        }`}>
                          {diagnosis.severity}
                        </span>
                      )}
                    </div>
                    
                    {diagnosis.urgency && (
                      <div className="mt-2">
                        <span className="text-sm text-gray-600">
                          Urgency: <span className="capitalize">{diagnosis.urgency}</span>
                        </span>
                      </div>
                    )}
                  </div>

                  {/* Prescription */}
                  <div className="ai-output-card green">
                    <h3 className="ai-output-title">Recommended Prescription</h3>
                    {typeof diagnosis.prescription === 'object' ? (
                      <div className="space-y-2">
                        <p className="ai-output-content">
                          <strong>Medication:</strong> {diagnosis.prescription.medication}
                        </p>
                        <p className="text-sm">
                          <strong>Dosage:</strong> {diagnosis.prescription.dosage}
                        </p>
                        <p className="text-sm">
                          <strong>Instructions:</strong> {diagnosis.prescription.instructions}
                        </p>
                      </div>
                    ) : (
                      <p className="ai-output-content">{diagnosis.prescription}</p>
                    )}
                  </div>

                  {/* Differential Diagnoses */}
                  {diagnosis.differential_diagnoses && diagnosis.differential_diagnoses.length > 0 && (
                    <div className="ai-output-card purple">
                      <h3 className="ai-output-title">Differential Diagnoses</h3>
                      <ul className="ai-output-list">
                        {diagnosis.differential_diagnoses.map((diff, index) => (
                          <li key={index}>{diff}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Red Flags */}
                  {diagnosis.red_flags && diagnosis.red_flags.length > 0 && (
                    <div className="ai-output-card red">
                      <h3 className="ai-output-title">⚠️ Red Flags</h3>
                      <ul className="ai-output-list">
                        {diagnosis.red_flags.map((flag, index) => (
                          <li key={index}>{flag}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Recommendations */}
                  {diagnosis.recommendations && diagnosis.recommendations.length > 0 && (
                    <div className="ai-output-card yellow">
                      <h3 className="ai-output-title">Care Recommendations</h3>
                      <ul className="ai-output-list">
                        {diagnosis.recommendations.map((rec, index) => (
                          <li key={index}>{rec}</li>
                        ))}
                      </ul>
                      {diagnosis.follow_up_days && (
                        <p className="text-sm text-gray-600 mt-2">
                          Follow-up recommended in {diagnosis.follow_up_days} days
                        </p>
                      )}
                    </div>
                  )}

                  {/* Patient Education */}
                  {diagnosis.patient_education && (
                    <div className="ai-output-card blue">
                      <h3 className="ai-output-title">Patient Education</h3>
                      <p className="ai-output-content">{diagnosis.patient_education}</p>
                    </div>
                  )}

                  {/* Clinical Notes */}
                  {diagnosis.notes && (
                    <div className="ai-output-card gray">
                      <h3 className="ai-output-title">Clinical Notes</h3>
                      <p className="ai-output-content">{diagnosis.notes}</p>
                    </div>
                  )}

                  {/* AI Model Information */}
                  <div className="ai-output-card purple">
                    <h3 className="ai-output-title">AI Analysis Details</h3>
                    {diagnosis.metadata ? (
                      <div className="space-y-1 text-sm">
                        <p><strong>Model Version:</strong> {diagnosis.metadata.model_version}</p>
                        <p><strong>Processing Time:</strong> {diagnosis.metadata.processing_time}ms</p>
                        <p><strong>Timestamp:</strong> {new Date(diagnosis.metadata.timestamp).toLocaleString()}</p>
                        {diagnosis.metadata.is_mock && (
                          <p className="text-orange-600"><strong>Note:</strong> Mock data (AI service unavailable)</p>
                        )}
                      </div>
                    ) : (
                      <p className="text-sm">
                        <strong>AI Model:</strong> {diagnosis.ai_model_version || 'MediChain-AI'}
                      </p>
                    )}
                  </div>

                  {/* Feedback Section */}
                  {!feedbackSubmitted && (
                    <div className="ai-output-card gray border-2 border-dashed">
                      <h3 className="ai-output-title">Provide Feedback</h3>
                      <p className="text-sm text-gray-600 mb-4">
                        Help improve our AI model by providing feedback on this diagnosis.
                      </p>
                      <div className="flex space-x-3">
                        <button
                          onClick={() => handleFeedback(true)}
                          className="flex items-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                        >
                          <ThumbsUp className="w-4 h-4 mr-2" />
                          Accurate
                        </button>
                        <button
                          onClick={() => handleFeedback(false)}
                          className="flex items-center px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
                        >
                          <ThumbsDown className="w-4 h-4 mr-2" />
                          Incorrect
                        </button>
                      </div>
                    </div>
                  )}

                  {feedbackSubmitted && (
                    <div className="ai-output-card green">
                      <h3 className="ai-output-title">✓ Feedback Submitted</h3>
                      <p className="text-sm">Thank you! Your feedback helps improve our AI model.</p>
                    </div>
                  )}
                </div>
              )}

              {!diagnosis && !loading && !error && (
                <div className="ai-empty-state">
                  <Brain className="ai-empty-icon" />
                  <p className="ai-empty-title">Enter patient symptoms to get AI diagnosis</p>
                  <p className="ai-empty-subtitle">
                    {aiStatus === 'connected' 
                      ? 'AI diagnosis service is ready' 
                      : 'Make sure the AI diagnosis server is running on port 5001'
                    }
                  </p>
                  {aiStatus === 'disconnected' && (
                    <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                      <div className="flex items-center">
                        <Info className="w-4 h-4 text-yellow-600 mr-2" />
                        <p className="text-sm text-yellow-800">
                          To start the AI service, run: <code className="bg-yellow-100 px-1 rounded">python ai_diagnosis.py</code>
                        </p>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>

          {/* System Information */}
          <div className="ai-system-info">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">Enhanced AI System Information</h3>
            <div className="ai-system-grid">
              <div className="ai-system-item">
                <Brain className="w-4 h-4 mr-2 text-blue-600" />
                <span><strong>AI Model:</strong> Random Forest with continuous learning</span>
              </div>
              <div className="ai-system-item">
                <Activity className="w-4 h-4 mr-2 text-purple-600" />
                <span><strong>Features:</strong> Treatment recommendations & personalized care</span>
              </div>
              <div className="ai-system-item">
                <FileText className="w-4 h-4 mr-2 text-green-600" />
                <span><strong>Feedback:</strong> Continuous learning from doctor feedback</span>
              </div>
              <div className="ai-system-item">
                <AlertCircle className="w-4 h-4 mr-2 text-red-600" />
                <span><strong>Safety:</strong> Medical disclaimers & red flag detection</span>
              </div>
              <div className="ai-system-item">
                <User className="w-4 h-4 mr-2 text-orange-600" />
                <span><strong>Integration:</strong> Patient data & blockchain records</span>
              </div>
              <div className="ai-system-item">
                <RefreshCw className="w-4 h-4 mr-2 text-teal-600" />
                <span><strong>Adaptability:</strong> Handles unknown symptoms intelligently</span>
              </div>
            </div>
            
            {/* AI Service Status */}
            <div className="mt-6 p-4 bg-gray-50 rounded-lg">
              <h4 className="font-medium text-gray-800 mb-2">Service Status</h4>
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <div className={`w-3 h-3 rounded-full mr-2 ${
                    aiStatus === 'connected' ? 'bg-green-500' :
                    aiStatus === 'disconnected' ? 'bg-red-500' :
                    'bg-yellow-500'
                  }`}></div>
                  <span className="text-sm">
                    AI Diagnosis Service: {aiStatus === 'connected' ? 'Connected' : 
                                         aiStatus === 'disconnected' ? 'Offline' : 'Checking...'}
                  </span>
                </div>
                <button
                  onClick={checkAiStatus}
                  className="text-sm text-blue-600 hover:text-blue-800 underline"
                >
                  Refresh Status
                </button>
              </div>
              
              {modelInfo && (
                <div className="mt-3 grid grid-cols-2 gap-4 text-sm text-gray-600">
                  <div>Model Version: {modelInfo.version}</div>
                  <div>Accuracy: {modelInfo.accuracy}%</div>
                  <div>Training Samples: {modelInfo.training_samples || 'N/A'}</div>
                  <div>Last Updated: {modelInfo.last_updated || 'Unknown'}</div>
                </div>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default AIAssistant;
