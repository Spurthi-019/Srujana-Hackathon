import React from 'react';
import './ClassroomStats.css';

interface StatCardProps {
  title: string;
  value: string | number;
  icon: React.ReactNode;
  color: string;
  change?: string;
  trend?: 'up' | 'down' | 'neutral';
}

const StatCard: React.FC<StatCardProps> = ({ title, value, icon, color, change, trend }) => (
  <div className={`stat-card ${color}`}>
    <div className="stat-icon">
      {icon}
    </div>
    <div className="stat-content">
      <div className="stat-value">{value}</div>
      <div className="stat-title">{title}</div>
      {change && (
        <div className={`stat-change ${trend}`}>
          {trend === 'up' && <span className="trend-icon">↗</span>}
          {trend === 'down' && <span className="trend-icon">↘</span>}
          {trend === 'neutral' && <span className="trend-icon">→</span>}
          {change}
        </div>
      )}
    </div>
  </div>
);

interface ProgressBarProps {
  label: string;
  value: number;
  max: number;
  color?: string;
}

const ProgressBar: React.FC<ProgressBarProps> = ({ label, value, max, color = 'primary' }) => {
  const percentage = (value / max) * 100;
  
  return (
    <div className="progress-container">
      <div className="progress-header">
        <span className="progress-label">{label}</span>
        <span className="progress-value">{value}/{max}</span>
      </div>
      <div className="progress-bar">
        <div 
          className={`progress-fill ${color}`}
          data-percentage={percentage}
        />
      </div>
    </div>
  );
};

interface ClassroomStatsProps {
  studentCount: number;
  attendanceRate: number;
  averageQuizScore: number;
  completedAssignments: number;
  totalAssignments: number;
}

const ClassroomStats: React.FC<ClassroomStatsProps> = ({
  studentCount,
  attendanceRate,
  averageQuizScore,
  completedAssignments,
  totalAssignments
}) => {
  const statsData = [
    {
      title: 'Total Students',
      value: studentCount,
      icon: (
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
          <path d="M17 21V19C17 17.9391 16.5786 16.9217 15.8284 16.1716C15.0783 15.4214 14.0609 15 13 15H5C3.93913 15 2.92172 15.4214 2.17157 16.1716C1.42143 16.9217 1 17.9391 1 19V21M13 7C13 9.20914 11.2091 11 9 11C6.79086 11 5 9.20914 5 7C5 4.79086 6.79086 3 9 3C11.2091 3 13 4.79086 13 7ZM24 21V19C23.9993 18.1137 23.7044 17.2528 23.1614 16.5523C22.6184 15.8519 21.8581 15.3516 21 15.13M17 3.13C17.8604 3.35031 18.623 3.85071 19.1676 4.55232C19.7122 5.25392 20.0078 6.11683 20.0078 7.005C20.0078 7.89317 19.7122 8.75608 19.1676 9.45768C18.623 10.1593 17.8604 10.6597 17 10.88" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
        </svg>
      ),
      color: 'blue',
      change: '+2 this week',
      trend: 'up' as const
    },
    {
      title: 'Attendance Rate',
      value: `${attendanceRate}%`,
      icon: (
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
          <path d="M9 12L11 14L15 10M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
        </svg>
      ),
      color: 'green',
      change: '+5%',
      trend: 'up' as const
    },
    {
      title: 'Avg Quiz Score',
      value: `${averageQuizScore}%`,
      icon: (
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
          <path d="M9 11H15M9 15H15M17 21L12 16L7 21V5C7 4.46957 7.21071 3.96086 7.58579 3.58579C7.96086 3.21071 8.46957 3 9 3H15C15.5304 3 16.0391 3.21071 16.4142 3.58579C16.7893 3.96086 17 4.46957 17 5V21Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
        </svg>
      ),
      color: 'purple',
      change: '+3%',
      trend: 'up' as const
    }
  ];

  return (
    <div className="classroom-stats">
      <div className="stats-grid">
        {statsData.map((stat, index) => (
          <StatCard
            key={index}
            title={stat.title}
            value={stat.value}
            icon={stat.icon}
            color={stat.color}
            change={stat.change}
            trend={stat.trend}
          />
        ))}
      </div>
      
      <div className="progress-section">
        <h3 className="progress-section-title">Class Progress</h3>
        <div className="progress-grid">
          <ProgressBar
            label="Assignments Completed"
            value={completedAssignments}
            max={totalAssignments}
            color="primary"
          />
          <ProgressBar
            label="Class Participation"
            value={Math.round(attendanceRate)}
            max={100}
            color="success"
          />
          <ProgressBar
            label="Average Performance"
            value={averageQuizScore}
            max={100}
            color="warning"
          />
        </div>
      </div>
    </div>
  );
};

export default ClassroomStats;