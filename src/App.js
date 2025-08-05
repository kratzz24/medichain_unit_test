import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import LandingPage from './pages/LandingPage';
import MedichainLogin from './frontend/MedichainLogin';
import './App.css';

// Create placeholder components
const Signup = () => (
  <div style={{ padding: '2rem', textAlign: 'center' }}>
    <h2>Signup Page</h2>
    <p>Signup component coming soon...</p>
  </div>
);

const Dashboard = () => (
  <div style={{ padding: '2rem', textAlign: 'center' }}>
    <h2>Dashboard</h2>
    <p>Dashboard component coming soon...</p>
  </div>
);

const ResetPassword = () => (
  <div style={{ padding: '2rem', textAlign: 'center' }}>
    <h2>Reset Password</h2>
    <p>Reset password component coming soon...</p>
  </div>
);

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="App">
          <Routes>
            {/* Landing page as the default route */}
            <Route path="/" element={<LandingPage />} />
            
            {/* Auth routes */}
            <Route path="/login" element={<MedichainLogin />} />
            <Route path="/signup" element={<Signup />} />
            <Route path="/reset-password" element={<ResetPassword />} />
            
            {/* Dashboard route */}
            <Route path="/dashboard" element={<Dashboard />} />
            
            {/* Redirect any unknown routes to landing page */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
