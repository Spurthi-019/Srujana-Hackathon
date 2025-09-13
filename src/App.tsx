
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { SignInButton, UserButton, useUser } from '@clerk/clerk-react';
import ThemeToggle from './components/ThemeToggle';
import LoadingSpinner from './components/LoadingSpinner';
import { ArrowRightIcon, UserIcon } from './components/AnimatedIcons';
import { useToast } from './contexts/ToastContext';
import './App.css';

const colleges = ['College of Engineering', 'College of Science', 'College of Arts'];
const blocks = ['Block A', 'Block B', 'Block C'];
const classrooms = ['Room 101', 'Room 102', 'Room 103'];


function generateUnifiedCode(college: string, block: string, classroom: string, teacherCode: string) {
  if (!college || !block || !classroom || !teacherCode) return '';
  // Simple code generation logic (can be replaced with real logic)
  return `${college.replace(/\s/g, '').slice(0,3).toUpperCase()}-${block.replace(/\s/g, '')}-${classroom.replace(/\s/g, '')}-${teacherCode}`;
}


function App() {
  const navigate = useNavigate();
  const { isSignedIn, isLoaded } = useUser();
  const { addToast } = useToast();
  const [selectedCollege, setSelectedCollege] = useState('');
  const [selectedBlock, setSelectedBlock] = useState('');
  const [selectedClassroom, setSelectedClassroom] = useState('');
  const [selectedTeacherCode, setSelectedTeacherCode] = useState('');
  const [isLoading, setIsLoading] = useState(false);

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
      // Simulate a brief loading period for better UX
      setTimeout(() => {
        navigate(`/classroom/${encodeURIComponent(unifiedCode)}`);
        setIsLoading(false);
      }, 800);
    }
  };

  if (!isLoaded) {
    return (
      <div className="loading-overlay">
        <LoadingSpinner size="large" color="white" text="Loading..." />
      </div>
    );
  }

  return (
    <div className="landing-container fade-in">
      <header className="landing-header">
        <div className="site-title scale-in">EduHub Pro</div>
        <div className="header-controls">
          <ThemeToggle />
          <div className="auth-buttons">
            {!isSignedIn ? (
              <SignInButton mode="modal">
                <button className="login-btn animate-on-hover">
                  <UserIcon size={18} className="mr-2" />
                  Sign In
                </button>
              </SignInButton>
            ) : (
              <UserButton 
                appearance={{
                  elements: {
                    avatarBox: "w-10 h-10"
                  }
                }}
              />
            )}
          </div>
        </div>
      </header>
      <main className="landing-main">
        <div className="dropdown-group stagger-container">
          <label>
            College:
            <select 
              value={selectedCollege} 
              onChange={e => setSelectedCollege(e.target.value)}
              className="animate-on-hover"
            >
              <option value="">Select College</option>
              {colleges.map(college => (
                <option key={college} value={college}>{college}</option>
              ))}
            </select>
          </label>
          <label>
            Block:
            <select 
              value={selectedBlock} 
              onChange={e => setSelectedBlock(e.target.value)}
              className="animate-on-hover"
            >
              <option value="">Select Block</option>
              {blocks.map(block => (
                <option key={block} value={block}>{block}</option>
              ))}
            </select>
          </label>
          <label>
            Classroom:
            <select 
              value={selectedClassroom} 
              onChange={e => setSelectedClassroom(e.target.value)}
              className="animate-on-hover"
            >
              <option value="">Select Classroom</option>
              {classrooms.map(classroom => (
                <option key={classroom} value={classroom}>{classroom}</option>
              ))}
            </select>
          </label>
          <label>
            Unified Teacher Code:
            <input
              type="text"
              className="teacher-code-input animate-on-hover"
              value={selectedTeacherCode}
              onChange={e => setSelectedTeacherCode(e.target.value)}
              placeholder="Enter Unified Teacher Code"
            />
          </label>
          {unifiedCode && (
            <div className="unified-code-box scale-in">
              <strong>Unified Code:</strong> <span>{unifiedCode}</span>
            </div>
          )}
          <button
            className="enter-class-btn animate-on-hover"
            onClick={handleEnterClass}
            disabled={!unifiedCode || isLoading}
          >
            {isLoading ? (
              <LoadingSpinner size="small" color="white" />
            ) : (
              <>
                Enter Class
                <ArrowRightIcon size={18} className="ml-2" />
              </>
            )}
          </button>
        </div>
      </main>
    </div>
  );
}

export default App;
