import React, { useEffect } from 'react';
import '../../mouse-bg-effect.css';
import './Dashboard.css';

interface DashboardProps {
  // Add props as needed
}

const Dashboard: React.FC<DashboardProps> = () => {
  useEffect(() => {
    const bg = document.querySelector('.mouse-bg-effect') as HTMLElement;
    const move = (e: MouseEvent) => {
      if (bg) {
        bg.style.setProperty('--x', `${e.clientX}px`);
        bg.style.setProperty('--y', `${e.clientY}px`);
      }
    };
    window.addEventListener('mousemove', move);
    return () => window.removeEventListener('mousemove', move);
  }, []);

  return (
    <>
      <div className="mouse-bg-effect"></div>
      <div className="dashboard">
        <h1>Dashboard</h1>
        <p>Welcome to your dashboard!</p>
      </div>
    </>
  );
};

export default Dashboard;