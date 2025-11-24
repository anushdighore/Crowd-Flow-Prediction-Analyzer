import React, { useState } from "react";
import { useAuth } from "../../context/AuthContext";
import "../../styles/LoginPage.css";

const LoginPage = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const { login } = useAuth();

  const handleSubmit = (e) => {
    e.preventDefault();
    setError("");

    if (!username.trim() || !password.trim()) {
      setError("Please enter both username and password");
      return;
    }

    if (username.length < 3) {
      setError("Username must be at least 3 characters");
      return;
    }

    if (password.length < 3) {
      setError("Password must be at least 3 characters");
      return;
    }

    const success = login(username, password);
    if (!success) {
      setError("Login failed. Please try again.");
    }
  };

  return (
    <div className="login-container">
      <div className="login-wrapper">
        <div className="login-box">
          <h1>Login</h1>

          <form onSubmit={handleSubmit} className="login-form">
            <div className="form-group">
              <label htmlFor="username">Email</label>
              <input
                id="username"
                type="text"
                placeholder="Enter email or username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                onFocus={() => setError("")}
              />
            </div>

            <div className="form-group">
              <label htmlFor="password">Password</label>
              <input
                id="password"
                type="password"
                placeholder="Enter password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                onFocus={() => setError("")}
              />
            </div>

            {error && <div className="error-message">{error}</div>}

            <button type="submit" className="login-button">
              Login
            </button>
          </form>

          <div className="register-link">
            <span>Don't have an account? </span>
            <a href="#register">Register</a>
          </div>

          <div className="demo-info">
            <p>
              <strong>Demo Credentials:</strong>
            </p>
            <p>Username: demo</p>
            <p>Password: demo123</p>
          </div>
        </div>

        <div className="login-image">
          <svg viewBox="0 0 400 600" xmlns="http://www.w3.org/2000/svg">
            <defs>
              <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop
                  offset="0%"
                  style={{ stopColor: "#d8b3d1", stopOpacity: 1 }}
                />
                <stop
                  offset="50%"
                  style={{ stopColor: "#b891c2", stopOpacity: 1 }}
                />
                <stop
                  offset="100%"
                  style={{ stopColor: "#7b68a6", stopOpacity: 1 }}
                />
              </linearGradient>
            </defs>

            {/* Wavy background shapes */}
            <path
              d="M 0,150 Q 100,100 200,120 T 400,150 L 400,0 L 0,0 Z"
              fill="url(#grad1)"
              opacity="0.8"
            />
            <path
              d="M 0,200 Q 100,180 200,210 T 400,200 L 400,150 Q 200,120 0,150 Z"
              fill="url(#grad1)"
              opacity="0.7"
            />
            <path
              d="M 0,280 Q 100,250 200,290 T 400,280 L 400,200 Q 200,210 0,200 Z"
              fill="url(#grad1)"
              opacity="0.6"
            />
            <path
              d="M 0,360 Q 100,330 200,370 T 400,360 L 400,280 Q 200,290 0,280 Z"
              fill="url(#grad1)"
              opacity="0.5"
            />
            <path
              d="M 0,450 Q 100,420 200,460 T 400,450 L 400,360 Q 200,370 0,360 Z"
              fill="url(#grad1)"
              opacity="0.4"
            />
            <path
              d="M 0,600 Q 100,550 200,580 T 400,600 L 400,450 Q 200,460 0,450 Z"
              fill="url(#grad1)"
              opacity="0.3"
            />
          </svg>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
