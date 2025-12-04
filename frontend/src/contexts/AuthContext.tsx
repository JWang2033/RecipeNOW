import { createContext, useContext, useState, useEffect, type ReactNode } from 'react';
import { authApi } from '../services/api';

interface LoginResult {
  success: boolean;
  requires2FA?: boolean;
}

interface AuthContextType {
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (phoneNumber: string, password: string) => Promise<LoginResult>;
  loginWith2FA: (phoneNumber: string, password: string, totpCode: string) => Promise<void>;
  register: (phoneNumber: string, username: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    setIsAuthenticated(!!token);
    setIsLoading(false);
  }, []);

  const login = async (phoneNumber: string, password: string): Promise<LoginResult> => {
    const response = await authApi.login(phoneNumber, password);
    
    // Check if 2FA is required
    if (response.requires_2fa) {
      return { success: false, requires2FA: true };
    }
    
    // Normal login - save token
    if (response.access_token) {
      localStorage.setItem('token', response.access_token);
      setIsAuthenticated(true);
    }
    
    return { success: true };
  };

  const loginWith2FA = async (phoneNumber: string, password: string, totpCode: string) => {
    const response = await authApi.loginWith2FA(phoneNumber, password, totpCode);
    localStorage.setItem('token', response.access_token);
    setIsAuthenticated(true);
  };

  const register = async (phoneNumber: string, username: string, password: string) => {
    await authApi.register(phoneNumber, username, password);
    // Auto-login after registration
    await login(phoneNumber, password);
  };

  const logout = () => {
    localStorage.removeItem('token');
    setIsAuthenticated(false);
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, isLoading, login, loginWith2FA, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

