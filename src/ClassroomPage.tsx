import { UserButton, useUser } from '@clerk/clerk-react';
import React, { useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import {
    GenerateQuizIcon,
    LeaderboardIcon,
    NotesIcon,
    TakeAttendanceIcon
} from './components/AnimatedIcons';
import Breadcrumb from './components/Breadcrumb';
import ThemeToggle from './components/ThemeToggle';


const ClassroomPage: React.FC = () => {
  const { code } = useParams<{ code: string }>();
  const { user } = useUser();
  const navigate = useNavigate();
  const [teacher, setTeacher] = useState('');
  const [subject, setSubject] = useState('');
  const [day, setDay] = useState('');
  const [time, setTime] = useState('');

  const classroomOptions = [
    {
      title: 'Take Attendance',
      icon: TakeAttendanceIcon,
      route: 'attendance',
      description: 'Mark student attendance',
      color: 'from-emerald-500 to-green-600',
      bgColor: 'bg-emerald-50',
      iconColor: 'text-emerald-600'
    },
    {
      title: 'Generate Quiz',
      icon: GenerateQuizIcon,
      route: 'quiz',
      description: 'Create interactive quizzes',
      color: 'from-blue-500 to-indigo-600',
      bgColor: 'bg-blue-50',
      iconColor: 'text-blue-600'
    },
    {
      title: 'Notes',
      icon: NotesIcon,
      route: 'notes',
      description: 'View class materials',
      color: 'from-amber-500 to-orange-600',
      bgColor: 'bg-amber-50',
      iconColor: 'text-amber-600'
    },
    {
      title: 'Leaderboard',
      icon: LeaderboardIcon,
      route: 'leaderboard',
      description: 'Student rankings',
      color: 'from-purple-500 to-pink-600',
      bgColor: 'bg-purple-50',
      iconColor: 'text-purple-600'
    }
  ];
  
  console.log('Classroom code:', code);
  
  return (
    <div className="modern-classroom-page">
      {/* Header Section */}
      <div className="classroom-header-modern">
        <Breadcrumb />
        <div className="header-content">
          <div className="welcome-section-modern">
            <h1 className="welcome-title">Welcome back, {user?.firstName || 'Student'}! 👋</h1>
            <p className="welcome-subtitle">Ready to dive into your classroom?</p>
          </div>
          <div className="header-controls-modern">
            <ThemeToggle />
            <UserButton 
              appearance={{
                elements: {
                  avatarBox: "w-10 h-10 rounded-full ring-2 ring-white shadow-lg"
                }
              }}
            />
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="classroom-content-modern">
        {/* Classroom Code Info - CRISP and Centered */}
        <div style={{ textAlign: 'center', marginBottom: '1.5rem', fontWeight: 600, fontSize: '1.15rem', color: '#3b3b3b' }}>
          Join your class instantly with the code
        </div>
        {/* Class Details Form */}
        <div className="class-details-section">
          <h2 className="section-title">Class Details</h2>
          <div className="details-grid">
            <div className="input-group">
              <label>Teacher</label>
              <input
                type="text"
                placeholder="Enter teacher name"
                value={teacher}
                onChange={e => setTeacher(e.target.value)}
                className="modern-input"
              />
            </div>
            <div className="input-group">
              <label>Subject</label>
              <input
                type="text"
                placeholder="Enter subject"
                value={subject}
                onChange={e => setSubject(e.target.value)}
                className="modern-input"
              />
            </div>
            <div className="input-group">
              <label>Day</label>
              <input
                type="text"
                placeholder="e.g., Monday"
                value={day}
                onChange={e => setDay(e.target.value)}
                className="modern-input"
              />
            </div>
            <div className="input-group">
              <label>Time</label>
              <input
                type="text"
                placeholder="e.g., 10:00 AM"
                value={time}
                onChange={e => setTime(e.target.value)}
                className="modern-input"
              />
            </div>
          </div>
        </div>

        {/* Classroom Actions */}
        <div className="actions-section">
          <h2 className="section-title">What would you like to do?</h2>
          <div className="actions-horizontal">
            {classroomOptions.map((option, index) => {
              const IconComponent = option.icon;
              return (
                <div 
                  key={option.route}
                  className="action-card-modern"
                  onClick={() => navigate(option.route)}
                >
                  <div className={`action-icon-wrapper ${option.bgColor}`}>
                    <IconComponent 
                      size={24} 
                      className={option.iconColor}
                    />
                  </div>
                  <div className="action-content">
                    <h3 className="action-title">{option.title}</h3>
                    <p className="action-description">{option.description}</p>
                  </div>
                  <div className="action-arrow">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                      <path d="M5 12H19M19 12L12 5M19 12L12 19" 
                            stroke="currentColor" 
                            strokeWidth="2" 
                            strokeLinecap="round" 
                            strokeLinejoin="round"/>
                    </svg>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ClassroomPage;
