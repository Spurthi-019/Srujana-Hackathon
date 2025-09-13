import React, { useState } from 'react';
import { useUser, UserButton } from '@clerk/clerk-react';
import { useNavigate } from 'react-router-dom';
import AttendanceSection from './components/Dashboard/AttendanceSection';
import MarksSection from './components/Dashboard/MarksSection';
import InteractionsSection from './components/Dashboard/InteractionsSection';
import LeaderboardSection from './components/Dashboard/LeaderboardSection';
import DocumentsSection from './components/Dashboard/DocumentsSection';
import './StudentDashboard.css';

const StudentDashboard: React.FC = () => {
  const { user } = useUser();
  const navigate = useNavigate();
  const [activeSection, setActiveSection] = useState('overview');

  const sectionData = {
    overview: { title: 'Dashboard Overview', icon: '📊' },
    attendance: { title: 'Attendance', icon: '📅' },
    marks: { title: 'Marks & Grades', icon: '📝' },
    interactions: { title: 'Class Interactions', icon: '💬' },
    leaderboard: { title: 'Leaderboard', icon: '🏆' },
    documents: { title: 'Documents & Help', icon: '📚' }
  };

  const renderActiveSection = () => {
    switch (activeSection) {
      case 'attendance':
        return <AttendanceSection />;
      case 'marks':
        return <MarksSection />;
      case 'interactions':
        return <InteractionsSection />;
      case 'leaderboard':
        return <LeaderboardSection />;
      case 'documents':
        return <DocumentsSection />;
      default:
        return <DashboardOverview />;
    }
  };

  const DashboardOverview = () => (
    <div className="dashboard-overview">
      <div className="overview-grid">
        <div className="overview-card attendance-card" onClick={() => setActiveSection('attendance')}>
          <div className="card-icon">📅</div>
          <div className="card-content">
            <h3>Attendance</h3>
            <div className="attendance-percentage">87%</div>
            <p>Overall attendance rate</p>
          </div>
        </div>

        <div className="overview-card marks-card" onClick={() => setActiveSection('marks')}>
          <div className="card-icon">📝</div>
          <div className="card-content">
            <h3>Latest Grade</h3>
            <div className="grade-display">A-</div>
            <p>Average performance</p>
          </div>
        </div>

        <div className="overview-card interactions-card" onClick={() => setActiveSection('interactions')}>
          <div className="card-icon">💬</div>
          <div className="card-content">
            <h3>Interactions</h3>
            <div className="interaction-count">24</div>
            <p>This week's participation</p>
          </div>
        </div>

        <div className="overview-card leaderboard-card" onClick={() => setActiveSection('leaderboard')}>
          <div className="card-icon">🏆</div>
          <div className="card-content">
            <h3>Class Rank</h3>
            <div className="rank-display">#3</div>
            <p>Out of 28 students</p>
          </div>
        </div>
      </div>

      <div className="recent-activity">
        <h3>Recent Activity</h3>
        <div className="activity-list">
          <div className="activity-item">
            <span className="activity-icon">✅</span>
            <div className="activity-content">
              <p>Attended Math class</p>
              <span className="activity-time">2 hours ago</span>
            </div>
          </div>
          <div className="activity-item">
            <span className="activity-icon">📝</span>
            <div className="activity-content">
              <p>Completed Physics Quiz</p>
              <span className="activity-time">1 day ago</span>
            </div>
          </div>
          <div className="activity-item">
            <span className="activity-icon">💬</span>
            <div className="activity-content">
              <p>Asked question in Chemistry</p>
              <span className="activity-time">2 days ago</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="student-dashboard">
      {/* Header */}
      <header className="dashboard-header">
        <div className="header-left">
          <button className="back-btn" onClick={() => navigate('/')}>
            ← Back to Home
          </button>
          <h1>Student Dashboard</h1>
        </div>
        <div className="header-right">
          <div className="user-info">
            <span>Welcome, {user?.firstName || 'Student'}!</span>
            <UserButton />
          </div>
        </div>
      </header>

      <div className="dashboard-content">
        {/* Sidebar Navigation */}
        <nav className="dashboard-sidebar">
          {Object.entries(sectionData).map(([key, section]) => (
            <button
              key={key}
              className={`nav-item ${activeSection === key ? 'active' : ''}`}
              onClick={() => setActiveSection(key)}
            >
              <span className="nav-icon">{section.icon}</span>
              <span className="nav-text">{section.title}</span>
            </button>
          ))}
        </nav>

        {/* Main Content */}
        <main className="dashboard-main">
          <div className="section-header">
            <h2>{sectionData[activeSection as keyof typeof sectionData]?.title}</h2>
          </div>
          <div className="section-content">
            {renderActiveSection()}
          </div>
        </main>
      </div>
    </div>
  );
};

export default StudentDashboard;