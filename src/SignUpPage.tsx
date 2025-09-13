import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './Auth.css';

const SignUpPage: React.FC = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');

  const handleSignUp = (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password || !confirmPassword) {
      setError('Please fill all fields.');
      return;
    }
    if (password !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }
    // On success, redirect to login page
    navigate('/login');
  };

  return (
    <div className="auth-container">
      <form className="auth-form" onSubmit={handleSignUp}>
        <h2>Sign Up</h2>
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
        <input
          type="password"
          placeholder="Confirm Password"
          value={confirmPassword}
          onChange={e => setConfirmPassword(e.target.value)}
          className="auth-input"
        />
        <button type="submit" className="auth-btn">Sign Up</button>
        <div className="auth-switch">
          Already have an account?{' '}
          <span className="auth-link" onClick={() => navigate('/login')}>Login</span>
        </div>
      </form>
    </div>
  );
};

export default SignUpPage;
