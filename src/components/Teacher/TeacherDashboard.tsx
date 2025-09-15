import { useUser } from '@clerk/clerk-react';
import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import '../../mouse-bg-effect.css';
import { apiService } from '../../services/api';
import ThemeToggle from '../ThemeToggle';
import './TeacherDashboard.css';

interface TeacherInfo {
  name: string;
  employeeId: string;
  department: string;
  subjects: string[];
  totalClasses: number;
  upcomingClasses: number;
}

interface ClassSchedule {
  id: string;
  subject: string;
  time: string;
  room: string;
  duration: string;
  students: number;
}

interface ScheduledHours {
  today: number;
  thisWeek: number;
  thisMonth: number;
  total: number;
}

const TeacherDashboard: React.FC = () => {
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
  const navigate = useNavigate();
  const { user, isLoaded } = useUser();
  const [activeTab, setActiveTab] = useState<'overview' | 'schedule' | 'classes'>('overview');
  const [teacherInfo, setTeacherInfo] = useState<TeacherInfo | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const loadTeacherData = async () => {
      if (!isLoaded) return;
      
      if (!user) {
        navigate('/');
        return;
      }

      try {
        // Set default data first to ensure component renders
        setTeacherInfo({
          name: user.fullName || user.firstName || 'Teacher',
          employeeId: user.id,
          department: 'Computer Science',
          subjects: ['Programming', 'Data Structures', 'Algorithms'],
          totalClasses: 5,
          upcomingClasses: 3
        });
        
        // Try to fetch real data from API (optional)
        try {
          const dashboardResponse = await apiService.getTeacherDashboard(user.id) as any;
          if (dashboardResponse) {
            setTeacherInfo(prev => ({
              ...prev!,
              totalClasses: dashboardResponse?.my_classes?.length || prev!.totalClasses,
              upcomingClasses: dashboardResponse?.my_classes?.filter((c: any) => c.is_active)?.length || prev!.upcomingClasses
            }));
          }
        } catch (apiError) {
          console.warn('API call failed, using default data:', apiError);
          // Continue with default data - don't throw
        }
        
      } catch (error) {
        console.error('Error loading teacher data:', error);
        // Even if everything fails, set basic data
        setTeacherInfo({
          name: user?.fullName || user?.firstName || 'Teacher',
          employeeId: user?.id || 'unknown',
          department: 'Computer Science',
          subjects: ['Programming'],
          totalClasses: 0,
          upcomingClasses: 0
        });
      } finally {
        setIsLoading(false);
      }
    };

    loadTeacherData();
  }, [user, isLoaded, navigate]);

  if (isLoading) {
    return (
      <div className="teacher-dashboard">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <h2>Loading Teacher Dashboard...</h2>
          <p>Preparing your classroom management tools</p>
        </div>
      </div>
    );
  }

  if (!teacherInfo) {
    return (
      <div className="teacher-dashboard">
        <div className="error-container">
          <h2>Unable to Load Dashboard</h2>
          <p>We're having trouble loading your dashboard data.</p>
          <button onClick={() => window.location.reload()} className="retry-btn">
            Try Again
          </button>
          <button onClick={() => navigate('/')} className="home-btn">
            Go Home
          </button>
        </div>
      </div>
    );
  }

  const todaySchedule: ClassSchedule[] = [
    {
      id: '1',
      subject: 'Data Structures',
      time: '09:00 AM - 10:30 AM',
      room: 'CS-101',
      duration: '90 mins',
      students: 45
    },
    {
      id: '2', 
      subject: 'Web Development',
      time: '11:00 AM - 12:30 PM',
      room: 'CS-205',
      duration: '90 mins',
      students: 38
    },
    {
      id: '3',
      subject: 'Algorithms',
      time: '02:00 PM - 03:30 PM', 
      room: 'CS-301',
      duration: '90 mins',
      students: 42
    }
  ];

  const scheduledHours: ScheduledHours = {
    today: 4.5,
    thisWeek: 18,
    thisMonth: 72,
    total: 450
  };

  const handleCreateClass = () => {
    navigate('/teacher/create-class');
  };

  const handleManageSchedule = () => {
    navigate('/teacher/schedule-planner');
  };

  const renderOverview = () => (
    <div className="teacher-overview">
      <div className="teacher-stats-grid">
        <div className="teacher-stat-card">
          <div className="stat-icon">📚</div>
          <div className="stat-content">
            <h3>{teacherInfo.totalClasses}</h3>
            <p>Total Classes</p>
          </div>
        </div>
        <div className="teacher-stat-card">
          <div className="stat-icon">⏰</div>
          <div className="stat-content">
            <h3>{teacherInfo.upcomingClasses}</h3>
            <p>Upcoming Classes</p>
          </div>
        </div>
        <div className="teacher-stat-card">
          <div className="stat-icon">👥</div>
          <div className="stat-content">
            <h3>{teacherInfo.subjects.length}</h3>
            <p>Subjects Teaching</p>
          </div>
        </div>
        <div className="teacher-stat-card">
          <div className="stat-icon">⏱️</div>
          <div className="stat-content">
            <h3>{scheduledHours.thisWeek}h</h3>
            <p>This Week</p>
          </div>
        </div>
      </div>

      <div className="teacher-info-card">
        <h3>Teacher Information</h3>
        <div className="teacher-details">
          <div className="detail-row">
            <span className="label">Name:</span>
            <span className="value">{teacherInfo.name}</span>
          </div>
          <div className="detail-row">
            <span className="label">Employee ID:</span>
            <span className="value">{teacherInfo.employeeId}</span>
          </div>
          <div className="detail-row">
            <span className="label">Department:</span>
            <span className="value">{teacherInfo.department}</span>
          </div>
          <div className="detail-row">
            <span className="label">Subjects:</span>
            <span className="value">{teacherInfo.subjects.join(', ')}</span>
          </div>
        </div>
      </div>
    </div>
  );

  const renderSchedule = () => (
    <div className="teacher-schedule">
      <div className="schedule-header">
        <h3>Today's Schedule</h3>
        <div className="schedule-date">
          {new Date().toLocaleDateString('en-US', { 
            weekday: 'long', 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric' 
          })}
        </div>
      </div>
      <div className="schedule-list">
        {todaySchedule.map((schedule) => (
          <div key={schedule.id} className="schedule-item">
            <div className="schedule-time">
              <div className="time">{schedule.time}</div>
              <div className="duration">{schedule.duration}</div>
            </div>
            <div className="schedule-content">
              <h4>{schedule.subject}</h4>
              <div className="schedule-details">
                <span className="room">📍 {schedule.room}</span>
                <span className="students">👥 {schedule.students} students</span>
              </div>
            </div>
            <div className="schedule-status">
              <div className="status-indicator upcoming"></div>
              <span>Upcoming</span>
            </div>
          </div>
        ))}
      </div>

      <div className="scheduled-hours-card">
        <h3>Scheduled Hours</h3>
        <div className="hours-grid">
          <div className="hour-item">
            <span className="hour-label">Today</span>
            <span className="hour-value">{scheduledHours.today}h</span>
          </div>
          <div className="hour-item">
            <span className="hour-label">This Week</span>
            <span className="hour-value">{scheduledHours.thisWeek}h</span>
          </div>
          <div className="hour-item">
            <span className="hour-label">This Month</span>
            <span className="hour-value">{scheduledHours.thisMonth}h</span>
          </div>
          <div className="hour-item">
            <span className="hour-label">Total</span>
            <span className="hour-value">{scheduledHours.total}h</span>
          </div>
        </div>
      </div>
    </div>
  );

  const renderClasses = () => (
    <div className="teacher-classes">
      <div className="classes-header">
        <h3>Class Management</h3>
        <p>Create and manage your classes, schedules, and course materials</p>
      </div>
      
      <div className="action-buttons">
        <button 
          className="create-class-btn enhanced-option"
          onClick={handleCreateClass}
        >
          <div className="option-icon-container">
            <span className="option-icon">➕</span>
          </div>
          <div className="option-content">
            <h3 className="option-title">Create Class</h3>
            <p className="option-description">Set up a new class with syllabus, notes, and schedule</p>
          </div>
          <span className="option-arrow">→</span>
        </button>

        <button 
          className="manage-schedule-btn enhanced-option"
          onClick={handleManageSchedule}
        >
          <div className="option-icon-container">
            <span className="option-icon">📅</span>
          </div>
          <div className="option-content">
            <h3 className="option-title">Manage Schedule</h3>
            <p className="option-description">Create and edit your teaching schedule and monthly planner</p>
          </div>
          <span className="option-arrow">→</span>
        </button>
      </div>

      <div className="existing-classes">
        <h4>Your Classes</h4>
        <div className="class-list">
          {teacherInfo.subjects.map((subject, index) => (
            <div key={index} className="class-card">
              <div className="class-info">
                <h5>{subject}</h5>
                <p>Class Code: CS_{subject.replace(/\s+/g, '')}_PS</p>
                <div className="class-stats">
                  <span>👥 35-45 students</span>
                  <span>📅 3 sessions/week</span>
                </div>
              </div>
              <div className="class-actions">
                <button className="edit-btn">Edit</button>
                <button className="view-btn">View</button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const renderContent = () => {
    switch (activeTab) {
      case 'overview':
        return renderOverview();
      case 'schedule':
        return renderSchedule();
      case 'classes':
        return renderClasses();
      default:
        return renderOverview();
    }
  };

  return (
    <div className="teacher-dashboard">
      <div className="dashboard-header">
        <div className="welcome-section">
          <h1>Welcome back, {teacherInfo.name.split(' ')[1] || teacherInfo.name}!</h1>
          <p>Manage your classes, schedules, and course materials</p>
        </div>
        <div className="header-actions">
          <ThemeToggle />
          <div className="notification-badge">
            <span className="badge-icon">🔔</span>
            <span className="badge-count">3</span>
          </div>
        </div>
      </div>

      <div className="dashboard-navigation">
        <button 
          className={`nav-tab ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          <span className="tab-icon">📊</span>
          Overview
        </button>
        <button 
          className={`nav-tab ${activeTab === 'schedule' ? 'active' : ''}`}
          onClick={() => setActiveTab('schedule')}
        >
          <span className="tab-icon">📅</span>
          Schedule
        </button>
        <button 
          className={`nav-tab ${activeTab === 'classes' ? 'active' : ''}`}
          onClick={() => setActiveTab('classes')}
        >
          <span className="tab-icon">🎓</span>
          Classes
        </button>
      </div>

      <div className="dashboard-content">
        {renderContent()}
      </div>
    </div>
  );
};

export default TeacherDashboard;