import React, { useState, useEffect } from 'react';
import Header from './Header';
import LoadingSpinner from '../components/LoadingSpinner';
import AIProgressBar from '../components/AIProgressBar';
import { showToast } from '../components/CustomToast';
import { Brain, User, Activity, FileText, RefreshCw, Plus, AlertCircle } from 'lucide-react';
import { patientService } from '../services/patientService';
import { useAuth } from '../context/AuthContext';
import '../assets/styles/AIAssistant.css';

const AIAssistant = () => {
  const [patients, setPatients] = useState([]);
  const [selectedPatient, setSelectedPatient] = useState('');
  const [symptoms, setSymptoms] = useState('');
  const [diagnosis, setDiagnosis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [loadingPatients, setLoadingPatients] = useState(true);
  const [error, setError] = useState(null);
  const [progress, setProgress] = useState(0);
  const [progressStatus, setProgressStatus] = useState('');
  const { user } = useAuth();

  useEffect(() => {
    loadPatients();
  }, []);

  const loadPatients = async () => {
    try {
      setLoadingPatients(true);
      const result = await patientService.getAllPatients();
      
      if (result.success) {
        setPatients(result.data);
      } else {
        showToast.error('Failed to load patients');
        // Fallback to sample data if API fails
        setPatients([
          { id: 1, patient_id: 'P001', name: 'John Doe', age: 35, gender: 'Male' },
          { id: 2, patient_id: 'P002', name: 'Jane Smith', age: 28, gender: 'Female' },
          { id: 3, patient_id: 'P003', name: 'Robert Johnson', age: 42, gender: 'Male' }
        ]);
      }
    } catch (err) {
      console.error('Error loading patients:', err);
      showToast.error('Error loading patients');
    } finally {
      setLoadingPatients(false);
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
    if (!selectedPatient || !symptoms.trim()) {
      showToast.error('Please select a patient and enter symptoms');
      return;
    }

    setLoading(true);
    setError(null);
    setDiagnosis(null);
    setProgress(0);
    
    // Start progress simulation
    await simulateProgress();

    try {
      const response = await fetch('http://localhost:5000/api/diagnose', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          patient_id: selectedPatient,
          symptoms: symptoms.trim(),
          patient_name: patients.find(p => p.patient_id === selectedPatient)?.name,
          patient_age: patients.find(p => p.patient_id === selectedPatient)?.age,
          patient_gender: patients.find(p => p.patient_id === selectedPatient)?.gender
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to get diagnosis');
      }

      const data = await response.json();
      setDiagnosis(data);
      showToast.success('AI diagnosis completed successfully');
    } catch (err) {
      console.error('Diagnosis error:', err);
      
      // Enhanced mock data with blockchain integration
      const selectedPatientData = patients.find(p => p.patient_id === selectedPatient);
      const mockDiagnosis = {
        diagnosis: 'Upper Respiratory Infection',
        prescription: 'Azithromycin 500mg once daily for 3 days',
        confidence: 85,
        recommendations: [
          'Rest for 2-3 days',
          'Stay hydrated',
          'Monitor temperature',
          'Follow up if symptoms worsen'
        ],
        severity: 'Mild',
        notes: 'Likely viral infection. Consider additional tests if fever persists beyond 3 days.',
        blockchain_hash: `0x${Math.random().toString(16).substr(2, 8)}...${Math.random().toString(16).substr(2, 6)}`,
        encrypted_data: true,
        ai_model_version: 'MediChain-AI-v2.1',
        network_speed: navigator.connection?.effectiveType || 'unknown',
        processing_time: calculateDelay()
      };
      
      setDiagnosis(mockDiagnosis);
      showToast.info('AI diagnosis completed (mock data - backend not connected)');
    } finally {
      setLoading(false);
      setTimeout(() => {
        setProgress(0);
        setProgressStatus('');
      }, 1000);
    }
  };

  const handleClear = () => {
    setSelectedPatient('');
    setSymptoms('');
    setDiagnosis(null);
    setError(null);
    setProgress(0);
    setProgressStatus('');
    showToast.info('Form cleared');
  };

  if (loadingPatients) {
    return (
      <div className="ai-assistant-container">
        <div className="background-crosses">
          {[...Array(12)].map((_, i) => (
            <span key={i} className={`cross cross-${i + 1}`}>
              <Plus size={24} />
            </span>
          ))}
        </div>
        <Header />
        <main className="ai-main-content">
          <div className="flex justify-center items-center h-64">
            <LoadingSpinner size="large" text="Loading patients..." />
          </div>
        </main>
      </div>
    );
  }

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
          </div>

          <div className="ai-grid">
            {/* Input Section */}
            <div className="ai-card">
              <div className="ai-card-header">
                <Activity className="w-6 h-6 mr-2 text-blue-600" />
                Patient Symptoms
              </div>

              <div className="space-y-6">
                {/* Patient Selection */}
                <div className="ai-form-group">
                  <label className="ai-label">
                    <User className="w-4 h-4 inline mr-1" />
                    Select Patient
                  </label>
                  <select
                    value={selectedPatient}
                    onChange={(e) => setSelectedPatient(e.target.value)}
                    className="ai-select"
                  >
                    <option value="">Choose a patient...</option>
                    {patients.map((patient) => (
                      <option key={patient.id} value={patient.patient_id}>
                        {patient.name} (ID: {patient.patient_id}, Age: {patient.age}, {patient.gender})
                      </option>
                    ))}
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
                    disabled={loading || !selectedPatient || !symptoms.trim()}
                    className="ai-primary-button"
                  >
                    {loading ? 'Processing...' : (
                      <>
                        <Brain className="w-5 h-5 mr-2" />
                        Run Diagnosis
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
                      {patients.find(p => p.patient_id === selectedPatient)?.name} 
                      (ID: {selectedPatient})
                    </p>
                  </div>

                  {/* Diagnosis */}
                  <div className="ai-output-card blue">
                    <h3 className="ai-output-title">AI Diagnosis</h3>
                    <p className="ai-output-content">{diagnosis.diagnosis}</p>
                    <div className="mt-2">
                      <span className="text-sm">
                        Confidence: {diagnosis.confidence}%
                      </span>
                    </div>
                  </div>

                  {/* Prescription */}
                  <div className="ai-output-card green">
                    <h3 className="ai-output-title">Recommended Prescription</h3>
                    <p className="ai-output-content">{diagnosis.prescription}</p>
                  </div>

                  {/* Blockchain Integration */}
                  <div className="ai-output-card purple">
                    <h3 className="ai-output-title">Blockchain Record</h3>
                    <p className="text-sm">
                      <strong>Hash:</strong> {diagnosis.blockchain_hash}
                    </p>
                    <p className="text-sm">
                      <strong>Encrypted:</strong> {diagnosis.encrypted_data ? 'Yes' : 'No'}
                    </p>
                    <p className="text-sm">
                      <strong>AI Model:</strong> {diagnosis.ai_model_version}
                    </p>
                    {diagnosis.network_speed && (
                      <p className="text-sm">
                        <strong>Network:</strong> {diagnosis.network_speed}
                      </p>
                    )}
                  </div>

                  {/* Recommendations */}
                  {diagnosis.recommendations && diagnosis.recommendations.length > 0 && (
                    <div className="ai-output-card yellow">
                      <h3 className="ai-output-title">Additional Recommendations</h3>
                      <ul className="ai-output-list">
                        {diagnosis.recommendations.map((rec, index) => (
                          <li key={index}>{rec}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Notes */}
                  {diagnosis.notes && (
                    <div className="ai-output-card gray">
                      <h3 className="ai-output-title">Clinical Notes</h3>
                      <p className="ai-output-content">{diagnosis.notes}</p>
                    </div>
                  )}

                  {/* Severity */}
                  {diagnosis.severity && (
                    <div className={`ai-output-card ${
                      diagnosis.severity === 'Critical' ? 'red' :
                      diagnosis.severity === 'Moderate' ? 'orange' : 'green'
                    }`}>
                      <h3 className="ai-output-title">Severity Level</h3>
                      <p className="ai-output-content">{diagnosis.severity}</p>
                    </div>
                  )}
                </div>
              )}

              {!diagnosis && !loading && !error && (
                <div className="ai-empty-state">
                  <Brain className="ai-empty-icon" />
                  <p className="ai-empty-title">Enter patient symptoms to get AI diagnosis</p>
                  <p className="ai-empty-subtitle">Make sure your local Flask backend is running</p>
                </div>
              )}
            </div>
          </div>

          {/* System Information */}
          <div className="ai-system-info">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">AI System Information</h3>
            <div className="ai-system-grid">
              <div className="ai-system-item">
                <Brain className="w-4 h-4 mr-2 text-blue-600" />
                <span><strong>AI Model:</strong> Custom-trained medical diagnosis</span>
              </div>
              <div className="ai-system-item">
                <Activity className="w-4 h-4 mr-2 text-purple-600" />
                <span><strong>Security:</strong> AES & SHA-256 encryption</span>
              </div>
              <div className="ai-system-item">
                <FileText className="w-4 h-4 mr-2 text-green-600" />
                <span><strong>Integration:</strong> Blockchain health records</span>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default AIAssistant;
