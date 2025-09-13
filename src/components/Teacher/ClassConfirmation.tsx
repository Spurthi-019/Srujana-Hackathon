import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import './ClassConfirmation.css';

interface ClassFormData {
  className: string;
  classLevel: string;
  subject: string;
  semester: string;
  department: string;
  syllabus: File | null;
  notes: File | null;
}

interface ScheduleEntry {
  day: string;
  topic: string;
  materials: File | null;
  notes: string;
}

interface LocationState {
  formData: ClassFormData;
  schedule: ScheduleEntry[];
  classCode: string;
}

const ClassConfirmation: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const state = location.state as LocationState;

  // If no state is passed, redirect back to create class
  if (!state) {
    navigate('/teacher/create-class');
    return null;
  }

  const { formData, schedule, classCode } = state;

  const handleBackToDashboard = () => {
    navigate('/teacher/dashboard');
  };

  const handleCreateAnother = () => {
    navigate('/teacher/create-class');
  };

  const formatScheduleCount = () => {
    const totalDays = schedule.length;
    const monthsSet = new Set(schedule.map(entry => entry.day.substring(0, 7)));
    const monthsCount = monthsSet.size;
    
    return {
      totalDays,
      monthsCount
    };
  };

  const { totalDays, monthsCount } = formatScheduleCount();

  return (
    <div className="class-confirmation">
      <div className="confirmation-container">
        <div className="success-animation">
          <div className="checkmark-circle">
            <div className="checkmark">✓</div>
          </div>
        </div>

        <div className="confirmation-content">
          <h1>Class Created Successfully!</h1>
          <p className="success-message">
            Your class has been created and is now ready for students to join.
          </p>

          <div className="class-code-section">
            <h2>Your Class Code</h2>
            <div className="class-code-display">
              <span className="class-code">{classCode}</span>
              <button 
                className="copy-button"
                onClick={() => navigator.clipboard.writeText(classCode)}
                title="Copy class code"
              >
                📋
              </button>
            </div>
            <p className="code-explanation">
              Share this code with your students to join the class
            </p>
          </div>

          <div className="class-summary">
            <h3>Class Summary</h3>
            <div className="summary-grid">
              <div className="summary-item">
                <span className="summary-label">Class Name:</span>
                <span className="summary-value">{formData.className}</span>
              </div>
              <div className="summary-item">
                <span className="summary-label">Subject:</span>
                <span className="summary-value">{formData.subject}</span>
              </div>
              <div className="summary-item">
                <span className="summary-label">Level:</span>
                <span className="summary-value">{formData.classLevel}</span>
              </div>
              <div className="summary-item">
                <span className="summary-label">Semester:</span>
                <span className="summary-value">{formData.semester}</span>
              </div>
              <div className="summary-item">
                <span className="summary-label">Department:</span>
                <span className="summary-value">{formData.department}</span>
              </div>
              <div className="summary-item">
                <span className="summary-label">Syllabus:</span>
                <span className="summary-value">
                  {formData.syllabus ? `✓ ${formData.syllabus.name}` : 'Not uploaded'}
                </span>
              </div>
              <div className="summary-item">
                <span className="summary-label">Course Notes:</span>
                <span className="summary-value">
                  {formData.notes ? `✓ ${formData.notes.name}` : 'Not uploaded'}
                </span>
              </div>
              <div className="summary-item">
                <span className="summary-label">Schedule:</span>
                <span className="summary-value">
                  {totalDays} days planned across {monthsCount} month{monthsCount !== 1 ? 's' : ''}
                </span>
              </div>
            </div>
          </div>

          <div className="schedule-preview">
            <h3>Schedule Overview</h3>
            <div className="schedule-stats">
              <div className="stat-card">
                <div className="stat-number">{totalDays}</div>
                <div className="stat-label">Total Days</div>
              </div>
              <div className="stat-card">
                <div className="stat-number">{monthsCount}</div>
                <div className="stat-label">Month{monthsCount !== 1 ? 's' : ''}</div>
              </div>
              <div className="stat-card">
                <div className="stat-number">{schedule.filter(entry => entry.materials).length}</div>
                <div className="stat-label">Materials</div>
              </div>
              <div className="stat-card">
                <div className="stat-number">{schedule.filter(entry => entry.notes.trim()).length}</div>
                <div className="stat-label">Notes</div>
              </div>
            </div>

            <div className="upcoming-topics">
              <h4>Next 5 Topics</h4>
              <div className="topics-list">
                {schedule.slice(0, 5).map((entry, index) => {
                  const date = new Date(entry.day);
                  const formattedDate = date.toLocaleDateString('en-US', { 
                    month: 'short', 
                    day: 'numeric' 
                  });
                  
                  return (
                    <div key={entry.day} className="topic-item">
                      <div className="topic-date">{formattedDate}</div>
                      <div className="topic-content">
                        <span className="topic-title">{entry.topic}</span>
                        <div className="topic-extras">
                          {entry.materials && <span className="has-material">📎</span>}
                          {entry.notes.trim() && <span className="has-notes">📝</span>}
                        </div>
                      </div>
                    </div>
                  );
                })}
                {schedule.length > 5 && (
                  <div className="more-topics">
                    +{schedule.length - 5} more topics planned
                  </div>
                )}
              </div>
            </div>
          </div>

          <div className="next-steps">
            <h3>Next Steps</h3>
            <div className="steps-list">
              <div className="step-item">
                <div className="step-icon">👥</div>
                <div className="step-content">
                  <h4>Share Class Code</h4>
                  <p>Give the class code to your students so they can join</p>
                </div>
              </div>
              <div className="step-item">
                <div className="step-icon">📅</div>
                <div className="step-content">
                  <h4>Start Teaching</h4>
                  <p>Begin following your planned schedule and upload materials</p>
                </div>
              </div>
              <div className="step-item">
                <div className="step-icon">📊</div>
                <div className="step-content">
                  <h4>Monitor Progress</h4>
                  <p>Track student attendance and engagement through the dashboard</p>
                </div>
              </div>
            </div>
          </div>

          <div className="action-buttons">
            <button className="secondary-button" onClick={handleCreateAnother}>
              Create Another Class
            </button>
            <button className="primary-button" onClick={handleBackToDashboard}>
              Back to Dashboard
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ClassConfirmation;