import React, { createContext, ReactNode, useContext, useEffect, useState } from 'react';

interface ThemeContextType {
  isDarkMode: boolean;
  toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

interface ThemeProviderProps {
  children: ReactNode;
}

export const ThemeProvider: React.FC<ThemeProviderProps> = ({ children }) => {
  // Check localStorage for saved theme preference, default to light mode
  const [isDarkMode, setIsDarkMode] = useState<boolean>(() => {
    const savedTheme = localStorage.getItem('theme');
    return savedTheme === 'dark';
  });

  // Apply theme to document root on mount and when theme changes
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', isDarkMode ? 'dark' : 'light');
    localStorage.setItem('theme', isDarkMode ? 'dark' : 'light');
    
    // Update CSS custom properties for theme
    const root = document.documentElement;
    
    if (isDarkMode) {
      // Dark theme variables
      root.style.setProperty('--bg-primary', 'linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%)');
      root.style.setProperty('--bg-secondary', 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)');
      root.style.setProperty('--bg-glass', 'rgba(255, 255, 255, 0.05)');
      root.style.setProperty('--bg-card', 'rgba(255, 255, 255, 0.08)');
      root.style.setProperty('--text-primary', '#ffffff');
      root.style.setProperty('--text-secondary', '#b8c2cc');
      root.style.setProperty('--text-muted', '#8892b0');
      root.style.setProperty('--accent-primary', '#4facfe');
      root.style.setProperty('--accent-secondary', '#00f2fe');
      root.style.setProperty('--accent-tertiary', '#ff77c7');
      root.style.setProperty('--border-color', 'rgba(255, 255, 255, 0.1)');
      root.style.setProperty('--shadow-sm', '0 2px 8px rgba(0, 0, 0, 0.3)');
      root.style.setProperty('--shadow-md', '0 4px 16px rgba(0, 0, 0, 0.4)');
      root.style.setProperty('--shadow-lg', '0 8px 32px rgba(0, 0, 0, 0.5)');
      root.style.setProperty('--shadow-glow', '0 0 20px rgba(79, 172, 254, 0.3)');
      root.style.setProperty('--gradient-primary', 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)');
      root.style.setProperty('--gradient-secondary', 'linear-gradient(135deg, #ff77c7 0%, #4facfe 100%)');
      root.style.setProperty('--gradient-card', 'linear-gradient(135deg, rgba(255, 255, 255, 0.08) 0%, rgba(255, 255, 255, 0.04) 100%)');
      root.style.setProperty('--gradient-mesh', 'radial-gradient(circle at 25% 25%, #4facfe 0%, transparent 50%), radial-gradient(circle at 75% 75%, #ff77c7 0%, transparent 50%)');
    } else {
      // Light theme variables
      root.style.setProperty('--bg-primary', 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 50%, #e0e6ec 100%)');
      root.style.setProperty('--bg-secondary', 'linear-gradient(135deg, #ffffff 0%, #f8fafc 100%)');
      root.style.setProperty('--bg-glass', 'rgba(255, 255, 255, 0.9)');
      root.style.setProperty('--bg-card', 'rgba(255, 255, 255, 0.95)');
      root.style.setProperty('--text-primary', '#1a202c');
      root.style.setProperty('--text-secondary', '#2d3748');
      root.style.setProperty('--text-muted', '#718096');
      root.style.setProperty('--accent-primary', '#3182ce');
      root.style.setProperty('--accent-secondary', '#00b4d8');
      root.style.setProperty('--accent-tertiary', '#e53e3e');
      root.style.setProperty('--border-color', 'rgba(0, 0, 0, 0.1)');
      root.style.setProperty('--shadow-sm', '0 2px 8px rgba(0, 0, 0, 0.1)');
      root.style.setProperty('--shadow-md', '0 4px 16px rgba(0, 0, 0, 0.15)');
      root.style.setProperty('--shadow-lg', '0 8px 32px rgba(0, 0, 0, 0.2)');
      root.style.setProperty('--shadow-glow', '0 0 20px rgba(49, 130, 206, 0.3)');
      root.style.setProperty('--gradient-primary', 'linear-gradient(135deg, #3182ce 0%, #00b4d8 100%)');
      root.style.setProperty('--gradient-secondary', 'linear-gradient(135deg, #e53e3e 0%, #3182ce 100%)');
      root.style.setProperty('--gradient-card', 'linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(248, 250, 252, 0.9) 100%)');
      root.style.setProperty('--gradient-mesh', 'radial-gradient(circle at 25% 25%, #3182ce 0%, transparent 50%), radial-gradient(circle at 75% 75%, #e53e3e 0%, transparent 50%)');
    }
  }, [isDarkMode]);

  const toggleTheme = () => {
    setIsDarkMode(prev => !prev);
  };

  return (
    <ThemeContext.Provider value={{ isDarkMode, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = (): ThemeContextType => {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};