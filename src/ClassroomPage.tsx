import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useUser, UserButton } from '@clerk/clerk-react';
import ThemeToggle from './components/ThemeToggle';
import Breadcrumb from './components/Breadcrumb';
import ClassroomStats from './components/ClassroomStats';
import { 
  TakeAttendanceIcon, 
  GenerateQuizIcon, 
  NotesIcon, 
  LeaderboardIcon 
} from './components/AnimatedIcons';


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
      description: 'Mark student attendance for today\'s class',
      color: 'attendance-icon',
      gradient: 'from-emerald-500 to-green-600'
    },
    {
      title: 'Generate Quiz',
      icon: GenerateQuizIcon,
      route: 'quiz',
      description: 'Create interactive quizzes for students',
      color: 'quiz-icon',
      gradient: 'from-blue-500 to-indigo-600'
    },
    {
      title: 'Notes',
      icon: NotesIcon,
      route: 'notes',
      description: 'View and manage class notes and materials',
      color: 'notes-icon',
      gradient: 'from-amber-500 to-orange-600'
    },
    {
      title: 'Class Leaderboard',
      icon: LeaderboardIcon,
      route: 'leaderboard',
      description: 'Track student performance and rankings',
      color: 'leaderboard-icon',
      gradient: 'from-red-500 to-pink-600'
    }
  ];
  
  console.log('Classroom code:', code); // Use the code variable
  return (
    <div className="classroom-page fade-in">
      <Breadcrumb />
      <div className="classroom-header">
        <div className="welcome-section">
          <h2 className="scale-in">Welcome, {user?.firstName || 'User'}!</h2>
          <p className="classroom-subtitle">Manage your classroom efficiently</p>
        </div>
        <div className="header-controls">
          <ThemeToggle />
          <UserButton 
            appearance={{
              elements: {
                avatarBox: "w-10 h-10"
              }
            }}
          />
        </div>
      </div>
      <div className="classroom-container">
        <ClassroomStats
          studentCount={32}
          attendanceRate={87}
          averageQuizScore={78}
          completedAssignments={15}
          totalAssignments={18}
        />
        <div className="classroom-form-row stagger-container">
          <input
            className="classroom-input animate-on-hover"
            type="text"
            placeholder="Enter Teacher Name"
            value={teacher}
            onChange={e => setTeacher(e.target.value)}
          />
          <input
            className="classroom-input animate-on-hover"
            type="text"
            placeholder="Enter Subject Name"
            value={subject}
            onChange={e => setSubject(e.target.value)}
          />
          <input
            className="classroom-input animate-on-hover"
            type="text"
            placeholder="Day"
            value={day}
            onChange={e => setDay(e.target.value)}
          />
          <input
            className="classroom-input animate-on-hover"
            type="text"
            placeholder="Time"
            value={time}
            onChange={e => setTime(e.target.value)}
          />
        </div>
        <div className="classroom-options stagger-container">
          {classroomOptions.map((option, index) => {
            const IconComponent = option.icon;
            return (
              <div 
                key={option.route}
                className={`classroom-option enhanced-option animate-on-hover option-${index}`}
                onClick={() => navigate(option.route)}
              >
                <div className="option-icon-container">
                  <IconComponent 
                    size={32} 
                    className={`${option.color} floating-icon`} 
                  />
                </div>
                <div className="option-content">
                  <h3 className="option-title">{option.title}</h3>
                  <p className="option-description">{option.description}</p>
                </div>
                <div className="option-arrow">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                    <path d="M5 12H19M19 12L12 5M19 12L12 19" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default ClassroomPage;
