
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { SignInButton, SignUpButton, UserButton, useUser } from '@clerk/clerk-react';
import ThemeToggle from './components/ThemeToggle';
import LoadingSpinner from './components/LoadingSpinner';
import { ArrowRightIcon, UserIcon, AcademicCapIcon, UserGroupIcon } from './components/AnimatedIcons';
import { useToast } from './contexts/ToastContext';
import './App.css';

const colleges = ['College of Engineering', 'College of Science', 'College of Arts'];
const blocks = ['Block A', 'Block B', 'Block C'];
const classrooms = ['Room 101', 'Room 102', 'Room 103'];

type UserRole = 'student' | 'teacher' | null;
type AuthMode = 'login' | 'signup';

function generateUnifiedCode(college: string, block: string, classroom: string, teacherCode: string) {
  if (!college || !block || !classroom || !teacherCode) return '';
  return `${college.replace(/\s/g, '').slice(0,3).toUpperCase()}-${block.replace(/\s/g, '')}-${classroom.replace(/\s/g, '')}-${teacherCode}`;
}

function App() {
  const navigate = useNavigate();
  const { isSignedIn, isLoaded, user } = useUser();
  const { addToast } = useToast();
  const [selectedCollege, setSelectedCollege] = useState('');
  const [selectedBlock, setSelectedBlock] = useState('');
  const [selectedClassroom, setSelectedClassroom] = useState('');
  const [selectedTeacherCode, setSelectedTeacherCode] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [selectedRole, setSelectedRole] = useState<UserRole>(null);
  const [authMode, setAuthMode] = useState<AuthMode>('login');

  const unifiedCode = generateUnifiedCode(selectedCollege, selectedBlock, selectedClassroom, selectedTeacherCode);

  const handleEnterClass = async () => {
    if (!isSignedIn) {
      addToast({
        message: 'Please sign in to access the classroom',
        type: 'warning',
        duration: 4000
      });
      return;
    }
    if (unifiedCode) {
      setIsLoading(true);
      addToast({
        message: 'Entering classroom...',
        type: 'info',
        duration: 2000
      });
      setTimeout(() => {
        navigate(`/classroom/${encodeURIComponent(unifiedCode)}`);
        setIsLoading(false);
      }, 800);
    }
  };

  const handleRoleSelect = (role: UserRole) => {
    setSelectedRole(role);
  };

  const AuthForm = ({ role }: { role: UserRole }) => {
    if (!role) return null;

    return (
      <div className="auth-form">
        <div className="auth-header">
          <div className="role-icon">
            {role === 'student' ? (
              <AcademicCapIcon size={32} />
            ) : (
              <UserGroupIcon size={32} />
            )}
          </div>
          <h3>{role === 'student' ? 'Student' : 'Teacher'} Portal</h3>
          <p>Welcome {role === 'student' ? 'students' : 'educators'}! Access your learning platform.</p>
        </div>

        <div className="auth-toggle">
          <button
            className={`auth-toggle-btn ${authMode === 'login' ? 'active' : ''}`}
            onClick={() => setAuthMode('login')}
          >
            Login
          </button>
          <button
            className={`auth-toggle-btn ${authMode === 'signup' ? 'active' : ''}`}
            onClick={() => setAuthMode('signup')}
          >
            Sign Up
          </button>
        </div>

        <div className="auth-buttons-container">
          {authMode === 'login' ? (
            <SignInButton 
              mode="modal"
              fallbackRedirectUrl={role === 'student' ? '/student/dashboard' : '/teacher/dashboard'}
            >
              <button className="auth-action-btn login-btn">
                <UserIcon size={20} />
                Login as {role === 'student' ? 'Student' : 'Teacher'}
              </button>
            </SignInButton>
          ) : (
            <SignUpButton 
              mode="modal"
              fallbackRedirectUrl={role === 'student' ? '/student/dashboard' : '/teacher/dashboard'}
            >
              <button className="auth-action-btn signup-btn">
                <UserIcon size={20} />
                Sign Up as {role === 'student' ? 'Student' : 'Teacher'}
              </button>
            </SignUpButton>
          )}
        </div>

        <div className="auth-features">
          <h4>What you'll get:</h4>
          <ul>
            {role === 'student' ? (
              <>
                <li>✓ Access to interactive lessons</li>
                <li>✓ Take quizzes and track progress</li>
                <li>✓ Submit assignments</li>
                <li>✓ Join virtual classrooms</li>
              </>
            ) : (
              <>
                <li>✓ Create and manage classrooms</li>
                <li>✓ Generate quizzes and assignments</li>
                <li>✓ Track student progress</li>
                <li>✓ Conduct virtual lectures</li>
              </>
            )}
          </ul>
        </div>

        <button 
          className="back-btn"
          onClick={() => setSelectedRole(null)}
        >
          ← Back to role selection
        </button>
      </div>
    );
  };

  const RoleSelector = () => (
    <div className="role-selector">
      <div className="role-header">
        <h2>Choose Your Role</h2>
        <p>Select whether you're joining as a student or teacher</p>
      </div>
      
      <div className="role-cards">
        <div 
          className="role-card student-card"
          onClick={() => handleRoleSelect('student')}
        >
          <div className="role-icon">
            <AcademicCapIcon size={48} />
          </div>
          <h3>Student</h3>
          <p>Access courses, take quizzes, and learn interactively</p>
          <div className="role-features">
            <span>• Interactive Learning</span>
            <span>• Progress Tracking</span>
            <span>• Quiz & Assignments</span>
          </div>
        </div>

        <div 
          className="role-card teacher-card"
          onClick={() => handleRoleSelect('teacher')}
        >
          <div className="role-icon">
            <UserGroupIcon size={48} />
          </div>
          <h3>Teacher</h3>
          <p>Create classrooms, manage students, and track progress</p>
          <div className="role-features">
            <span>• Classroom Management</span>
            <span>• Student Analytics</span>
            <span>• Content Creation</span>
          </div>
        </div>
      </div>
    </div>
  );

  if (!isLoaded) {
    return (
      <div className="loading-container">
        <LoadingSpinner />
      </div>
    );
  }

  return (
    <div className="landing-container">
      <header className="landing-header">
        <div className="site-title">EduHub Pro</div>
        <div className="header-controls">
          <ThemeToggle />
          {isSignedIn && (
            <UserButton 
              appearance={{
                elements: {
                  avatarBox: "w-10 h-10"
                }
              }}
            />
          )}
        </div>
      </header>

      <main className="landing-main">
        <div className="main-content">
          {/* Left Section - Classroom Entry */}
          <div className="classroom-section">
            <div className="section-header">
              <h1>Enter Classroom</h1>
              <p>Join your virtual classroom with the classroom code</p>
            </div>

            <div className="classroom-form">
              <div className="form-group">
                <label>College</label>
                <select 
                  value={selectedCollege} 
                  onChange={e => setSelectedCollege(e.target.value)}
                  className="form-select"
                  aria-label="Select College"
                >
                  <option value="">Select College</option>
                  {colleges.map(college => (
                    <option key={college} value={college}>{college}</option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label>Block</label>
                <select 
                  value={selectedBlock} 
                  onChange={e => setSelectedBlock(e.target.value)}
                  className="form-select"
                  aria-label="Select Block"
                >
                  <option value="">Select Block</option>
                  {blocks.map(block => (
                    <option key={block} value={block}>{block}</option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label>Classroom</label>
                <select 
                  value={selectedClassroom} 
                  onChange={e => setSelectedClassroom(e.target.value)}
                  className="form-select"
                  aria-label="Select Classroom"
                >
                  <option value="">Select Classroom</option>
                  {classrooms.map(classroom => (
                    <option key={classroom} value={classroom}>{classroom}</option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label>Teacher Code</label>
                <input
                  type="text"
                  className="form-input"
                  value={selectedTeacherCode}
                  onChange={e => setSelectedTeacherCode(e.target.value)}
                  placeholder="Enter Unified Teacher Code"
                />
              </div>

              {unifiedCode && (
                <div className="unified-code-display">
                  <span className="code-label">Classroom Code:</span>
                  <span className="code-value">{unifiedCode}</span>
                </div>
              )}

              <button
                className="enter-classroom-btn"
                onClick={handleEnterClass}
                disabled={!unifiedCode || isLoading}
              >
                {isLoading ? (
                  <LoadingSpinner size="small" color="white" />
                ) : (
                  <>
                    Enter Classroom
                    <ArrowRightIcon size={20} />
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Right Section - Authentication */}
          <div className="auth-section">
            {!isSignedIn ? (
              selectedRole ? (
                <AuthForm role={selectedRole} />
              ) : (
                <RoleSelector />
              )
            ) : (
              <div className="user-welcome">
                <div className="welcome-content">
                  <UserIcon size={64} />
                  <h2>Welcome back!</h2>
                  <p>Hello, {user?.firstName || 'User'}!</p>
                  <div className="user-actions">
                    <button 
                      className="dashboard-btn"
                      onClick={() => navigate('/student/dashboard')}
                    >
                      Go to Dashboard
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
