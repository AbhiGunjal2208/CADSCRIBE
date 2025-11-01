import React, { createContext, useContext, useState, useEffect } from 'react';
import { authAPI } from '@/api';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  const isAuthenticated = !!user;

  useEffect(() => {
    // Listen for logout events
    const handleLogout = () => {
      setUser(null);
      setIsLoading(false);
    };

    window.addEventListener('auth:logout', handleLogout);

    // Check for existing session on mount
    const checkAuth = async () => {
      // Only check auth if there's a token in localStorage
      const token = localStorage.getItem('cadscribe_token');
      
      if (!token) {
        // No token, user is not authenticated
        setUser(null);
        setIsLoading(false);
        return;
      }

      try {
        const response = await authAPI.getCurrentUser();
        if (response.data) {
          setUser(response.data);
        }
      } catch (error) {
        // Only log unexpected errors (not 401/403 which are normal when not authenticated)
        if (error.response?.status !== 401 && error.response?.status !== 403) {
          console.error('Failed to fetch user:', error);
        }
        // For 401/403, clear invalid token and set user to null
        if (error.response?.status === 401 || error.response?.status === 403) {
          localStorage.removeItem('cadscribe_token');
        }
        setUser(null);
      } finally {
        setIsLoading(false);
      }
    };

    checkAuth();
    return () => window.removeEventListener('auth:logout', handleLogout);
  }, []);

  const login = async (email, password) => {
    try {
      const response = await authAPI.login({ email, password });
      setUser(response.data.user);
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    }
  };

  const signup = async (email, password, name) => {
    try {
      const response = await authAPI.signup({ email, password, name });
      // Persist access token like in login flow so subsequent API calls are authenticated
      if (response.data?.access_token) {
        localStorage.setItem('cadscribe_token', response.data.access_token);
      }
      setUser(response.data.user);
    } catch (error) {
      console.error('Signup failed:', error);
      throw error;
    }
  };

  const logout = async () => {
    try {
      await authAPI.logout();
      setUser(null);
      window.dispatchEvent(new Event('auth:logout'));
    } catch (error) {
      console.error('Logout failed:', error);
      throw error;
    }
  };

  const loginDemo = async () => {
    try {
      const response = await authAPI.demoLogin();
      // Save the real token from backend
      if (response.data?.access_token) {
        localStorage.setItem('cadscribe_token', response.data.access_token);
      }
      setUser(response.data.user);
    } catch (error) {
      console.error('Demo login failed:', error);
      throw error;
    }
  };

  return (
    <AuthContext.Provider value={{
      user,
      isAuthenticated,
      isLoading,
      login,
      signup,
      logout,
      loginDemo
    }}>
      {children}
    </AuthContext.Provider>
  );
};
