import React, { createContext, useContext, useState, useEffect } from "react";

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  // DEMO MODE: Set to true to bypass authentication
  const DEMO_MODE = true;

  const [isAuthenticated, setIsAuthenticated] = useState(DEMO_MODE);
  const [user, setUser] = useState(
    DEMO_MODE ? { username: "demo", loginTime: new Date().toISOString() } : null
  );

  // Check localStorage on mount
  useEffect(() => {
    if (DEMO_MODE) {
      // In demo mode, always authenticate
      setIsAuthenticated(true);
      setUser({ username: "demo", loginTime: new Date().toISOString() });
      return;
    }

    const storedAuth = localStorage.getItem("isAuthenticated");
    const storedUser = localStorage.getItem("user");
    if (storedAuth === "true" && storedUser) {
      setIsAuthenticated(true);
      setUser(JSON.parse(storedUser));
    }
  }, []);

  const login = (username, password) => {
    // Simple validation - in a real app, this would call a backend API
    if (username && password) {
      const userData = { username, loginTime: new Date().toISOString() };
      setIsAuthenticated(true);
      setUser(userData);
      localStorage.setItem("isAuthenticated", "true");
      localStorage.setItem("user", JSON.stringify(userData));
      return true;
    }
    return false;
  };

  const logout = () => {
    setIsAuthenticated(false);
    setUser(null);
    localStorage.removeItem("isAuthenticated");
    localStorage.removeItem("user");
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
};
