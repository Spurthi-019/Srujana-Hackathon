
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
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
  const [selectedCollege, setSelectedCollege] = useState('');
  const [selectedBlock, setSelectedBlock] = useState('');
  const [selectedClassroom, setSelectedClassroom] = useState('');
  const [selectedTeacherCode, setSelectedTeacherCode] = useState('');

  const unifiedCode = generateUnifiedCode(selectedCollege, selectedBlock, selectedClassroom, selectedTeacherCode);

  const handleEnterClass = () => {
    if (unifiedCode) {
      window.open(`/classroom/${encodeURIComponent(unifiedCode)}`, '_blank');
    }
  };

  return (
    <div className="landing-container">
      <header className="landing-header">
        <div className="site-title">My Website Name</div>
        <div className="auth-buttons">
          <button className="login-btn" onClick={() => navigate('/login')}>Login</button>
          <button className="signup-btn" onClick={() => navigate('/signup')}>Sign Up</button>
        </div>
      </header>
      <main className="landing-main">
        <div className="dropdown-group">
          <label>
            College:
            <select value={selectedCollege} onChange={e => setSelectedCollege(e.target.value)}>
              <option value="">Select College</option>
              {colleges.map(college => (
                <option key={college} value={college}>{college}</option>
              ))}
            </select>
          </label>
          <label>
            Block:
            <select value={selectedBlock} onChange={e => setSelectedBlock(e.target.value)}>
              <option value="">Select Block</option>
              {blocks.map(block => (
                <option key={block} value={block}>{block}</option>
              ))}
            </select>
          </label>
          <label>
            Classroom:
            <select value={selectedClassroom} onChange={e => setSelectedClassroom(e.target.value)}>
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
              className="teacher-code-input"
              value={selectedTeacherCode}
              onChange={e => setSelectedTeacherCode(e.target.value)}
              placeholder="Enter Unified Teacher Code"
            />
          </label>
          {unifiedCode && (
            <div className="unified-code-box">
              <strong>Unified Code:</strong> <span>{unifiedCode}</span>
            </div>
          )}
          <button
            className="enter-class-btn"
            onClick={handleEnterClass}
            disabled={!unifiedCode}
          >
            Enter Class
          </button>
        </div>
      </main>
    </div>
  );
}

export default App;
