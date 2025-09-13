import React from 'react';
import './NavBar.css';

interface NavBarProps {
  // Add props as needed
}

const NavBar: React.FC<NavBarProps> = () => {
  return (
    <nav className="navbar">
      <div className="navbar-container">
        <div className="navbar-brand">
          <h2>Srujana Hackathon</h2>
        </div>
        <div className="navbar-nav">
          {/* Add navigation items here */}
        </div>
      </div>
    </nav>
  );
};

export default NavBar;