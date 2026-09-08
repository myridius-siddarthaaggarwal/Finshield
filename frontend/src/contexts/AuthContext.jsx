import React, { createContext, useContext, useState, useEffect } from 'react';
import { authApi } from '../services/api';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [currentUser, setCurrentUser] = useState({
    id: 8,
    full_name: 'Rahul Mehta',
    email: 'rahul.mehta@bank.com',
    role: 'ANALYST',
    division: 'FCRM / Compliance',
    title: 'Senior FCRM Risk Analyst'
  });
  const [allUsers, setAllUsers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadUsers();
  }, []);

  const loadUsers = async () => {
    try {
      const res = await authApi.getUsers();
      setAllUsers(res.data);
      // If default user found in db, set it
      const defaultUser = res.data.find(u => u.email === 'rahul.mehta@bank.com') || res.data[0];
      if (defaultUser) {
        setCurrentUser(defaultUser);
      }
    } catch (err) {
      console.warn('Backend offline or loading demo fallback:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSwitchPersona = async (userId) => {
    try {
      const res = await authApi.switchPersona(userId);
      setCurrentUser(res.data.user);
      if (res.data.access_token) {
        localStorage.setItem('finshield_token', res.data.access_token);
      }
    } catch (err) {
      // Fallback local switch
      const localUser = allUsers.find(u => u.id === userId);
      if (localUser) setCurrentUser(localUser);
    }
  };

  return (
    <AuthContext.Provider value={{
      currentUser,
      allUsers,
      switchPersona: handleSwitchPersona,
      loading
    }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
