'use client';

import { createContext, useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { auth } from '@/utils/api';

interface User {
  username: string;
  email: string;
  is_admin: boolean;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (username: string, password: string) => Promise<boolean>;
  logout: () => Promise<boolean>;
  isAuthenticated: boolean;
  isAdmin: boolean;
}

export const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  const fetchUser = useCallback(async () => {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        throw new Error('No access token');
      }
      const { data } = await auth.me();
      if (!data) {
        throw new Error('No user data returned');
      }
      setUser({
        username: data.username,
        email: data.email,
        is_admin: data.is_admin
      });
      return true;
    } catch (error) {
      console.error('Failed to fetch user:', error);
      setUser(null);
      // Don't clear tokens here - let the API interceptor handle token management
      return false;
    } finally {
      setLoading(false);
    }
  }, []);

  const login = async (username: string, password: string) => {
    console.log('AuthProvider: Starting login process...');
    try {
      setLoading(true);
      console.log('AuthProvider: Calling auth.login...');
      const { data } = await auth.login(username, password);
      console.log('AuthProvider: Received response:', data);
      
      if (!data.access || !data.username || !data.email) {
        console.log('AuthProvider: Invalid response data');
        throw new Error('Invalid response data');
      }
      
      // Store tokens
      if (data.access) localStorage.setItem('access_token', data.access);
      if (data.refresh) localStorage.setItem('refresh_token', data.refresh);
      
      // Set user state
      console.log('AuthProvider: Setting user state...');
      const newUser = {
        username: data.username,
        email: data.email,
        is_admin: false // Default to false, will be updated by fetchUser
      };
      setUser(newUser);
      
      // Fetch complete user data to get admin status
      const fetchSuccess = await fetchUser();
      if (!fetchSuccess) {
        throw new Error('Failed to fetch user data');
      }
      
      // Redirect using router for better Next.js integration
      console.log('AuthProvider: User state set, redirecting...');
      router.replace('/dashboard/workspaces');
      return true;
    } catch (error) {
      console.error('Login failed:', error);
      return false;
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    try {
      setLoading(true);
      await auth.logout();
      setUser(null);
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      router.replace('/login');
      return true;
    } catch (error) {
      console.error('Logout failed:', error);
      return false;
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      setLoading(false);
      if (window.location.pathname !== '/login') {
        router.replace('/login');
      }
      return;
    }
    fetchUser().catch(() => {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      router.replace('/login');
    });
  }, [fetchUser, router]);

  return (
    <AuthContext.Provider value={{
      user,
      loading,
      login,
      logout,
      isAuthenticated: !!user,
      isAdmin: !!user?.is_admin,
    }}>
      {children}
    </AuthContext.Provider>
  );
}
