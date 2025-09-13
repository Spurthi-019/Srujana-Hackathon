import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './Auth.css';

const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    // Dummy validation
    if (!email || !password) {
      setError('Please enter both email and password.');
      return;
    }
    // On success, redirect to landing page
    navigate('/');
  };

  return (
    <div className="auth-container">
      <form className="auth-form" onSubmit={handleLogin}>
        <h2>Login</h2>
        {error && <div className="auth-error">{error}</div>}
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={e => setEmail(e.target.value)}
          className="auth-input"
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={e => setPassword(e.target.value)}
          className="auth-input"
        />
        <button type="submit" className="auth-btn">Login</button>
        <div className="auth-switch">
          Don't have an account?{' '}
          <span className="auth-link" onClick={() => navigate('/signup')}>Sign Up</span>
        </div>
      </form>
    </div>
  );
};

export default LoginPage;
