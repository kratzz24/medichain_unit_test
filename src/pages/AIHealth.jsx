import React, { useState, useEffect } from 'react';
import { Brain, User, Activity, FileText, AlertCircle, Info, LogIn, UserPlus, Database, Shield } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import LoadingSpinner from '../components/LoadingSpinner';
import AIProgressBar from '../components/AIProgressBar';
import { showToast } from '../components/CustomToast';
import { aiService } from '../services/aiService';
import { useAuth } from '../context/AuthContext';
import '../assets/styles/ModernDashboard.css';
import '../assets/styles/AIHealth.css';

const AIHealth = () => {
  const [symptoms, setSymptoms] = useState('');
  const [patientAge, setPatientAge] = useState('');
  const [patientGender, setPatientGender] = useState('');
  const [diagnosis, setDiagnosis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [progress, setProgress] = useState(0);
  const [progressStatus, setProgressStatus] = useState('');
  const [aiStatus, setAiStatus] = useState('checking');
  const [saveData, setSaveData] = useState(false);
  const [showAuthPrompt, setShowAuthPrompt] = useState(false);
  const [sessionData, setSessionData] = useState(null);
  
  const { user } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    checkAiStatus();
  }, []);

  const checkAiStatus = async () => {
    const healthCheck = await aiService.healthCheck();
    setAiStatus(healthCheck.status);
    if (!healthCheck.success) {
      console.warn('AI service unavailable:', healthCheck.error);
    }
  };

  // Network-aware delay calculation
  const calculateDelay = () => {
    const connection = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
    let baseDelay = 3000;
    
    if (connection) {
      if (connection.effectiveType === '2g') {
        baseDelay += 4000;
      } else if (connection.effectiveType === '3g') {
        baseDelay += 2000;
      } else if (connection.effectiveType === '4g') {
        baseDelay += 1000;
      }
    }
    
    return Math.max(baseDelay, 3000);
  };

  // Progress simulation
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

    // If user wants to save data but isn't logged in, show auth prompt
    if (saveData && !user) {
      setShowAuthPrompt(true);
      return;
    }

    setLoading(true);
    setError(null);
    setDiagnosis(null);
    setProgress(0);
    
    // Start progress simulation
    await simulateProgress();

    try {
      const diagnosisRequest = {
        symptoms: symptoms.trim(),
        patient_data: {
          age: parseInt(patientAge),
          gender: patientGender,
          patient_id: user ? user.id : `guest_${Date.now()}`,
          name: user ? `${user.first_name} ${user.last_name}` : 'Guest'
        },
        doctor_id: null, // No doctor for public access
        include_recommendations: true,
        detailed_analysis: true,
        save_to_database: saveData && user, // Only save if user is logged in and wants to save
        session_type: user ? 'authenticated' : 'guest'
      };

      console.log('Sending diagnosis request:', diagnosisRequest);
      
      const result = await aiService.getDiagnosis(diagnosisRequest);
      
      if (result.success) {
        setDiagnosis(result.data);
        setSessionData({
          symptoms,
          age: patientAge,
          gender: patientGender,
          timestamp: new Date().toISOString(),
          saved: saveData && user
        });
        showToast.success('AI diagnosis completed successfully');
        
        if (saveData && user) {
          showToast.info('Your diagnosis has been saved to your medical record');
        }
      } else {
        throw new Error(result.error || 'Failed to get diagnosis');
      }
      
    } catch (err) {
      console.error('Diagnosis error:', err);
      setError(err.message);
      
      if (aiStatus === 'disconnected') {
        showToast.error('AI service is unavailable. Please try again later.');
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

  const handleNewDiagnosis = () => {
    setSymptoms('');
    setPatientAge('');
    setPatientGender('');
    setDiagnosis(null);
    setError(null);
    setSaveData(false);
    setShowAuthPrompt(false);
    setSessionData(null);
  };

  const handleSignup = () => {
    navigate('/signup');
  };

  const handleLogin = () => {
    navigate('/login');
  };

  const closeAuthPrompt = () => {
    setShowAuthPrompt(false);
    setSaveData(false);
  };

  return (
    <div className="ai-assistant-container">
      {/* Background crosses */}
      <div className="background-crosses">
        {[...Array(24)].map((_, i) => (
          <span key={i} className={`cross cross-${i + 1}`}>
            +
          </span>
        ))}
      </div>

      {/* Simple Header for standalone page */}
      <header className="ai-health-header">
        <div className="header-left">
          <div className="logo-container">
            <div>MEDICHAIN AI</div>
          </div>
        </div>
        <div className="header-right">
          {!user && (
            <>
              <button onClick={handleLogin} className="auth-btn login-btn">
                <LogIn size={16} /> Login
              </button>
              <button onClick={handleSignup} className="auth-btn signup-btn">
                <UserPlus size={16} /> Sign Up
              </button>
            </>
          )}
          {user && (
            <div className="user-info">
              Welcome, {user.first_name}!
            </div>
          )}
        </div>
      </header>

      <main className="ai-assistant-main">
        <div className="ai-assistant-header">
          <div className="ai-title-section">
            <Brain size={32} className="ai-float" />
            <h1 className="ai-title">MediChain AI Health Assistant</h1>
            <p className="ai-subtitle">
              Get instant AI-powered health insights and recommendations
            </p>
          </div>
        </div>

        {/* Data Privacy Notice */}
        <div className="privacy-notice">
          <Info size={20} />
          <div className="privacy-text">
            <strong>Privacy Information:</strong> Your data is processed securely. 
            {!user && " For guest users, data is not saved after session ends."}
            {user && " As a registered user, you can choose to save your consultation history."}
          </div>
        </div>

        <div className="ai-assistant-content">
          <div className="ai-form-container">
            <div className="symptom-input-section">
              <h3>
                <User size={20} />
                Patient Information
              </h3>
              
              <div className="patient-info-grid">
                <div className="form-group">
                  <label>Age</label>
                  <input
                    type="number"
                    value={patientAge}
                    onChange={(e) => setPatientAge(e.target.value)}
                    placeholder="Enter age"
                    min="1"
                    max="120"
                    className="form-input"
                  />
                </div>
                
                <div className="form-group">
                  <label>Gender</label>
                  <select
                    value={patientGender}
                    onChange={(e) => setPatientGender(e.target.value)}
                    className="form-input"
                  >
                    <option value="">Select gender</option>
                    <option value="male">Male</option>
                    <option value="female">Female</option>
                    <option value="other">Other</option>
                  </select>
                </div>
              </div>

              <div className="form-group">
                <label>Symptoms</label>
                <textarea
                  value={symptoms}
                  onChange={(e) => setSymptoms(e.target.value)}
                  placeholder="Please describe your symptoms in detail..."
                  rows={6}
                  className="form-textarea"
                />
              </div>

              {/* Save Data Option */}
              {user && (
                <div className="save-data-option">
                  <label className="checkbox-container">
                    <input
                      type="checkbox"
                      checked={saveData}
                      onChange={(e) => setSaveData(e.target.checked)}
                    />
                    <span className="checkmark"></span>
                    <span className="checkbox-text">
                      <Database size={16} />
                      Save this consultation to my medical record
                    </span>
                  </label>
                  <div className="save-data-info">
                    <Shield size={14} />
                    Saved consultations can be reviewed by your doctor during appointments
                  </div>
                </div>
              )}

              {!user && (
                <div className="guest-notice">
                  <AlertCircle size={16} />
                  <span>
                    You're using MediChain as a guest. Your consultation will not be saved. 
                    <button onClick={handleSignup} className="link-button">
                      Create an account
                    </button> to save your medical history.
                  </span>
                </div>
              )}

              <button
                onClick={handleDiagnosis}
                disabled={loading}
                className="diagnose-btn"
              >
                {loading ? (
                  <>
                    <LoadingSpinner size="small" />
                    Analyzing...
                  </>
                ) : (
                  <>
                    <Brain size={20} />
                    Get AI Diagnosis
                  </>
                )}
              </button>
            </div>

            {/* Progress Bar */}
            {loading && (
              <div className="progress-section">
                <AIProgressBar progress={progress} status={progressStatus} />
              </div>
            )}

            {/* AI Status */}
            <div className={`ai-status ai-status-${aiStatus}`}>
              <Activity size={16} />
              AI Status: {aiStatus === 'connected' ? 'Online' : 'Checking...'}
            </div>
          </div>

          {/* Results Section */}
          {diagnosis && (
            <div className="diagnosis-results">
              <h3>
                <FileText size={20} />
                AI Diagnosis Results
              </h3>
              
              <div className="diagnosis-content">
                <div className="diagnosis-section">
                  <h4>Primary Diagnosis</h4>
                  <p>{diagnosis.diagnosis}</p>
                </div>
                
                <div className="diagnosis-section">
                  <h4>Confidence Level</h4>
                  <div className="confidence-bar">
                    <div 
                      className="confidence-fill" 
                      style={{ width: `${diagnosis.confidence}%` }}
                    ></div>
                    <span className="confidence-text">{diagnosis.confidence}%</span>
                  </div>
                </div>
                
                {diagnosis.prescription && (
                  <div className="diagnosis-section">
                    <h4>Recommended Treatment</h4>
                    <p>{diagnosis.prescription}</p>
                  </div>
                )}
                
                {diagnosis.recommendations && (
                  <div className="diagnosis-section">
                    <h4>Additional Recommendations</h4>
                    <p>{diagnosis.recommendations}</p>
                  </div>
                )}
                
                <div className="medical-disclaimer">
                  <AlertCircle size={16} />
                  <span>
                    <strong>Medical Disclaimer:</strong> This AI diagnosis is for informational purposes only 
                    and should not replace professional medical advice. Please consult with a qualified 
                    healthcare provider for proper medical evaluation and treatment.
                  </span>
                </div>

                {sessionData && (
                  <div className="session-info">
                    {sessionData.saved ? (
                      <div className="saved-notice">
                        <Database size={16} />
                        <span>This consultation has been saved to your medical record</span>
                      </div>
                    ) : (
                      <div className="not-saved-notice">
                        <AlertCircle size={16} />
                        <span>This consultation was not saved and will be lost when you leave this page</span>
                      </div>
                    )}
                  </div>
                )}
              </div>
              
              <button onClick={handleNewDiagnosis} className="new-diagnosis-btn">
                New Consultation
              </button>
            </div>
          )}

          {error && (
            <div className="error-message">
              <AlertCircle size={20} />
              <span>{error}</span>
            </div>
          )}
        </div>
      </main>

      {/* Auth Prompt Modal */}
      {showAuthPrompt && (
        <div className="modal-overlay">
          <div className="auth-prompt-modal">
            <h3>Account Required</h3>
            <p>To save your consultation history, you need to create an account or log in.</p>
            <div className="auth-prompt-actions">
              <button onClick={handleSignup} className="auth-btn signup-btn">
                <UserPlus size={16} /> Create Account
              </button>
              <button onClick={handleLogin} className="auth-btn login-btn">
                <LogIn size={16} /> Log In
              </button>
              <button onClick={closeAuthPrompt} className="auth-btn cancel-btn">
                Continue as Guest
              </button>
            </div>
          </div>
        </div>
      )}

      <style jsx>{`
        .ai-health-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 1rem 2rem;
          background: rgba(255, 255, 255, 0.95);
          backdrop-filter: blur(10px);
          border-bottom: 1px solid #e0e0e0;
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          z-index: 1000;
        }

        .logo-container {
          font-size: 1.5rem;
          font-weight: bold;
          color: #00d4aa;
        }

        .header-right {
          display: flex;
          align-items: center;
          gap: 1rem;
        }

        .auth-btn {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          padding: 0.5rem 1rem;
          border: none;
          border-radius: 6px;
          cursor: pointer;
          font-weight: 500;
          transition: all 0.3s ease;
        }

        .login-btn {
          background: transparent;
          color: #333;
          border: 1px solid #ddd;
        }

        .login-btn:hover {
          background: #f5f5f5;
        }

        .signup-btn {
          background: #00d4aa;
          color: white;
        }

        .signup-btn:hover {
          background: #00b899;
        }

        .user-info {
          color: #333;
          font-weight: 500;
        }

        .ai-assistant-main {
          margin-top: 80px;
          padding: 2rem;
        }

        .privacy-notice {
          display: flex;
          align-items: flex-start;
          gap: 0.75rem;
          background: #e8f5ff;
          border: 1px solid #00d4aa;
          border-radius: 8px;
          padding: 1rem;
          margin-bottom: 2rem;
          color: #333;
        }

        .privacy-text {
          line-height: 1.5;
        }

        .save-data-option {
          margin: 1rem 0;
          padding: 1rem;
          background: #f8f9fa;
          border-radius: 8px;
          border: 1px solid #e9ecef;
        }

        .checkbox-container {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          cursor: pointer;
          margin-bottom: 0.5rem;
        }

        .checkbox-text {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          font-weight: 500;
          color: #333;
        }

        .save-data-info {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          font-size: 0.9rem;
          color: #666;
          margin-left: 1.5rem;
        }

        .guest-notice {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          background: #fff3cd;
          border: 1px solid #ffeaa7;
          border-radius: 6px;
          padding: 0.75rem;
          margin: 1rem 0;
          font-size: 0.9rem;
          color: #856404;
        }

        .link-button {
          background: none;
          border: none;
          color: #00d4aa;
          text-decoration: underline;
          cursor: pointer;
          font-weight: 500;
          margin: 0 0.25rem;
        }

        .session-info {
          margin-top: 1rem;
          padding: 0.75rem;
          border-radius: 6px;
        }

        .saved-notice {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          background: #d4edda;
          border: 1px solid #c3e6cb;
          border-radius: 6px;
          padding: 0.75rem;
          color: #155724;
        }

        .not-saved-notice {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          background: #fff3cd;
          border: 1px solid #ffeaa7;
          border-radius: 6px;
          padding: 0.75rem;
          color: #856404;
        }

        .modal-overlay {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(0, 0, 0, 0.5);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 2000;
        }

        .auth-prompt-modal {
          background: white;
          border-radius: 12px;
          padding: 2rem;
          max-width: 400px;
          width: 90%;
          text-align: center;
        }

        .auth-prompt-modal h3 {
          color: #333;
          margin-bottom: 1rem;
        }

        .auth-prompt-modal p {
          color: #666;
          margin-bottom: 2rem;
          line-height: 1.5;
        }

        .auth-prompt-actions {
          display: flex;
          flex-direction: column;
          gap: 0.75rem;
        }

        .cancel-btn {
          background: #6c757d;
          color: white;
        }

        .cancel-btn:hover {
          background: #5a6268;
        }
      `}</style>
    </div>
  );
};

export default AIHealth;
