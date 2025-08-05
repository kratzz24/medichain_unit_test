import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext();

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
    const checkExistingAuth = () => {
      try {
        const token = localStorage.getItem('medichain_token');
        const userData = localStorage.getItem('medichain_user');
        
        if (token && userData) {
          setUser(JSON.parse(userData));
          setIsAuthenticated(true);
        }
      } catch (error) {
        console.error('Error checking existing auth:', error);
        localStorage.removeItem('medichain_token');
        localStorage.removeItem('medichain_user');
      } finally {
        setLoading(false);
      }
    };

    checkExistingAuth();
  }, []);

  const login = async (email, password) => {
    setLoading(true);
    setError(null);
    
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Mock authentication - replace with real API call
      if (email && password) {
        const mockUser = {
          id: 1,
          email: email,
          name: email.split('@')[0],
          role: email.includes('admin') ? 'admin' : 
                email.includes('doctor') ? 'doctor' : 'patient',
          avatar: null,
          createdAt: new Date().toISOString()
        };

        const mockToken = `mock_token_${Date.now()}`;
        
        // Store in localStorage
        localStorage.setItem('medichain_token', mockToken);
        localStorage.setItem('medichain_user', JSON.stringify(mockUser));
        
        setUser(mockUser);
        setIsAuthenticated(true);
        
        return { 
          success: true, 
          message: 'Login successful',
          user: mockUser,
          token: mockToken
        };
      } else {
        setError('Invalid credentials');
        return { 
          success: false, 
          message: 'Please enter both email and password' 
        };
      }
    } catch (error) {
      const errorMessage = 'Login failed. Please try again.';
      setError(errorMessage);
      return { 
        success: false, 
        message: errorMessage 
      };
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    // Clear localStorage
    localStorage.removeItem('medichain_token');
    localStorage.removeItem('medichain_user');
    
    // Reset state
    setIsAuthenticated(false);
    setUser(null);
    setError(null);
  };

  const register = async (userData) => {
    setLoading(true);
    setError(null);
    
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // Mock registration
      const mockUser = {
        id: Date.now(),
        email: userData.email,
        name: userData.name || userData.email.split('@')[0],
        role: userData.role || 'patient',
        avatar: null,
        createdAt: new Date().toISOString()
      };

      const mockToken = `mock_token_${Date.now()}`;
      
      // Store in localStorage
      localStorage.setItem('medichain_token', mockToken);
      localStorage.setItem('medichain_user', JSON.stringify(mockUser));
      
      setUser(mockUser);
      setIsAuthenticated(true);
      
      return { 
        success: true, 
        message: 'Registration successful',
        user: mockUser,
        token: mockToken
      };
    } catch (error) {
      const errorMessage = 'Registration failed. Please try again.';
      setError(errorMessage);
      return { 
        success: false, 
        message: errorMessage 
      };
    } finally {
      setLoading(false);
    }
  };

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
    register,
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