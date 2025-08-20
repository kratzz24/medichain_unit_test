import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

// Create the authentication context
const AuthContext = createContext();

// API base URL - point to your Flask backend
const API_URL = 'http://localhost:5000/api';

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Check for existing authentication on mount
  useEffect(() => {
    const checkExistingAuth = async () => {
      try {
        const token = localStorage.getItem('medichain_token');
        if (!token) {
          setLoading(false);
          return;
        }

        // If token exists, verify with backend
        const response = await axios.get(`${API_URL}/auth/verify`, {
          headers: {
            Authorization: `Bearer ${token}`
          }
        });

        if (response.data.success) {
          setUser(response.data.user);
          setIsAuthenticated(true);
        } else {
          // Clear invalid token
          localStorage.removeItem('medichain_token');
          localStorage.removeItem('medichain_user');
        }
      } catch (error) {
        console.error('Auth check error:', error);
        localStorage.removeItem('medichain_token');
        localStorage.removeItem('medichain_user');
      } finally {
        setLoading(false);
      }
    };

    checkExistingAuth();
  }, []);

  // Login function
  const login = async (email, password) => {
    setLoading(true);
    setError(null);
    
    try {
      // Try to connect to backend first
      try {
        const response = await axios.post(`${API_URL}/auth/login`, {
          email,
          password
        });
        
        if (response.data.success) {
          localStorage.setItem('medichain_token', response.data.token);
          localStorage.setItem('medichain_user', JSON.stringify(response.data.user));
          
          setUser(response.data.user);
          setIsAuthenticated(true);
          
          return { 
            success: true, 
            message: 'Login successful',
            user: response.data.user
          };
        } else {
          throw new Error(response.data.error || 'Login failed');
        }
      } catch (apiError) {
        console.log('Backend connection failed, using fallback mock login');
        
        // Fallback to mock login if backend is not available
        // Check if the user exists in localStorage from signup
        const storedUsers = JSON.parse(localStorage.getItem('medichain_users') || '[]');
        const user = storedUsers.find(u => u.email === email);
        
        if (user && user.password === password) {
          const mockToken = `mock_token_${Date.now()}`;
          
          localStorage.setItem('medichain_token', mockToken);
          localStorage.setItem('medichain_user', JSON.stringify(user));
          
          setUser(user);
          setIsAuthenticated(true);
          
          return { 
            success: true, 
            message: 'Login successful (mock)',
            user: user
          };
        } else {
          throw new Error('Invalid email or password');
        }
      }
    } catch (error) {
      setError(error.message || 'Login failed');
      return { 
        success: false, 
        message: error.message || 'Login failed' 
      };
    } finally {
      setLoading(false);
    }
  };

  // Signup function
  const signup = async (email, password, firstName, lastName, userType) => {
    setLoading(true);
    setError(null);
    
    try {
      // First try to connect to backend
      try {
        const response = await axios.post(`${API_URL}/auth/register`, {
          email,
          password,
          name: `${firstName} ${lastName}`,
          role: userType
        });
        
        if (response.data.success) {
          localStorage.setItem('medichain_token', response.data.token);
          localStorage.setItem('medichain_user', JSON.stringify(response.data.user));
          
          setUser(response.data.user);
          setIsAuthenticated(true);
          
          return { 
            success: true, 
            message: 'Account created successfully!',
            user: response.data.user
          };
        } else {
          throw new Error(response.data.error || 'Signup failed');
        }
      } catch (apiError) {
        console.log('Backend connection failed, using fallback mock signup');
        
        // Fallback to mock signup if backend is not available
        const storedUsers = JSON.parse(localStorage.getItem('medichain_users') || '[]');
        
        // Check if user already exists
        if (storedUsers.some(u => u.email === email)) {
          throw new Error('User already exists');
        }
        
        // Create new user
        const newUser = {
          id: Date.now(),
          email,
          password, // In a real app, never store plain passwords
          name: `${firstName} ${lastName}`,
          role: userType,
          created_at: new Date().toISOString()
        };
        
        // Add user to stored users
        storedUsers.push(newUser);
        localStorage.setItem('medichain_users', JSON.stringify(storedUsers));
        
        // Auto login
        const mockToken = `mock_token_${Date.now()}`;
        localStorage.setItem('medichain_token', mockToken);
        localStorage.setItem('medichain_user', JSON.stringify(newUser));
        
        setUser(newUser);
        setIsAuthenticated(true);
        
        return { 
          success: true, 
          message: 'Account created successfully! (mock)',
          user: newUser
        };
      }
    } catch (error) {
      setError(error.message || 'Signup failed');
      return { 
        success: false, 
        error: error.message || 'Signup failed' 
      };
    } finally {
      setLoading(false);
    }
  };

  // Logout function
  const logout = () => {
    localStorage.removeItem('medichain_token');
    localStorage.removeItem('medichain_user');
    setIsAuthenticated(false);
    setUser(null);
    setError(null);
  };

  // Update user function
  const updateUser = (updatedData) => {
    const updatedUser = { ...user, ...updatedData };
    setUser(updatedUser);
    localStorage.setItem('medichain_user', JSON.stringify(updatedUser));
  };

  const clearError = () => {
    setError(null);
  };

  const value = {
    isAuthenticated,
    user,
    loading,
    error,
    login,
    logout,
    signup,
    updateUser,
    clearError
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext;
