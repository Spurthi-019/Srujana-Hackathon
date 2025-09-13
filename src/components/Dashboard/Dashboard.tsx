import React from 'react';

interface DashboardProps {
  // Add props as needed
}

const Dashboard: React.FC<DashboardProps> = () => {
  return (
    <div className="dashboard">
      <h1>Dashboard</h1>
      <p>Welcome to your dashboard!</p>
    </div>
  );
};

export default Dashboard;