import React, { useEffect, useState } from 'react';
import './ThemeToggle.css';

const ThemeToggle: React.FC = () => {
  const [theme, setTheme] = useState<'light' | 'dark' | 'system'>('system');
  const [currentTheme, setCurrentTheme] = useState<'light' | 'dark'>('light');

  useEffect(() => {
    // Get theme from localStorage or default to system
    const savedTheme = localStorage.getItem('theme') as 'light' | 'dark' | 'system' || 'system';
    setTheme(savedTheme);
    
    // Apply theme
    applyTheme(savedTheme);
    
    // Listen for system theme changes
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    const handleSystemThemeChange = () => {
      if (theme === 'system') {
        const systemTheme = mediaQuery.matches ? 'dark' : 'light';
        setCurrentTheme(systemTheme);
        document.documentElement.removeAttribute('data-theme');
      }
    };
    
    mediaQuery.addEventListener('change', handleSystemThemeChange);
    
    return () => mediaQuery.removeEventListener('change', handleSystemThemeChange);
  }, [theme]);

  const applyTheme = (selectedTheme: 'light' | 'dark' | 'system') => {
    if (selectedTheme === 'system') {
      const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
      setCurrentTheme(systemTheme);
      document.documentElement.removeAttribute('data-theme');
    } else {
      setCurrentTheme(selectedTheme);
      document.documentElement.setAttribute('data-theme', selectedTheme);
    }
  };

  const handleThemeChange = (newTheme: 'light' | 'dark' | 'system') => {
    setTheme(newTheme);
    localStorage.setItem('theme', newTheme);
    applyTheme(newTheme);
  };

  const cycleTheme = () => {
    const themes: ('light' | 'dark' | 'system')[] = ['light', 'dark', 'system'];
    const currentIndex = themes.indexOf(theme);
    const nextTheme = themes[(currentIndex + 1) % themes.length];
    handleThemeChange(nextTheme);
  };

  const getThemeIcon = () => {
    switch (theme) {
      case 'light':
        return (
          <svg className="theme-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="5"/>
            <path d="M12 1v2m0 18v2M4.22 4.22l1.42 1.42m12.72 12.72l1.42 1.42M1 12h2m18 0h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/>
          </svg>
        );
      case 'dark':
        return (
          <svg className="theme-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
          </svg>
        );
      case 'system':
        return (
          <svg className="theme-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <rect x="2" y="4" width="20" height="16" rx="2"/>
            <path d="M2 8h20"/>
          </svg>
        );
    }
  };

  const getThemeLabel = () => {
    switch (theme) {
      case 'light': return 'Light';
      case 'dark': return 'Dark';
      case 'system': return 'System';
    }
  };

  return (
    <button
      onClick={cycleTheme}
      className={`theme-toggle premium ${theme} ${currentTheme}`}
      aria-label={`Current theme: ${getThemeLabel()}. Click to cycle themes.`}
      title={`Switch theme (Current: ${getThemeLabel()})`}
    >
      <div className="theme-toggle-content">
        {getThemeIcon()}
        <span className="theme-label">{getThemeLabel()}</span>
      </div>
      <div className="theme-indicator">
        <div className={`indicator ${currentTheme}`}></div>
      </div>
    </button>
  );
};

export default ThemeToggle;