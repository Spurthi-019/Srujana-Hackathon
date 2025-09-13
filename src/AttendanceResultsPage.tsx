import React from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { useToast } from './contexts/ToastContext';
import './AttendanceResultsPage.css';

interface Student {
  id: string;
  name: string;
  rollNumber: string;
  profileImage?: string;
}

interface AttendanceRecord {
  studentId: string;
  name: string;
  rollNumber: string;
  timestamp: Date;
  confidence: number;
}

interface AttendanceSession {
  sessionId: string;
  classroomCode: string;
  timeSlot: number;
  maxStudents: number;
  detectedStudents: AttendanceRecord[];
  isActive: boolean;
  startTime: Date;
}

interface LocationState {
  session: AttendanceSession;
  presentStudents: AttendanceRecord[];
  absentStudents: Student[];
}

const AttendanceResultsPage: React.FC = () => {
  const { code } = useParams<{ code: string }>();
  const navigate = useNavigate();
  const location = useLocation();
  const { addToast } = useToast();
  
  const state = location.state as LocationState;
  
  if (!state) {
    // Redirect back if no data is available
    navigate(`/classroom/${code}/attendance`);
    return null;
  }
  
  const { session, presentStudents, absentStudents } = state;
  
  const totalStudents = presentStudents.length + absentStudents.length;
  const attendancePercentage = totalStudents > 0 ? (presentStudents.length / totalStudents) * 100 : 0;
  
  const handleSaveAttendance = async () => {
    try {
      // Here you would make the API call to save attendance to backend
      const attendanceData = {
        sessionId: session.sessionId,
        classroomCode: session.classroomCode,
        date: session.startTime.toISOString().split('T')[0],
        timeSlot: session.timeSlot,
        presentStudents: presentStudents.map(student => ({
          studentId: student.studentId,
          timestamp: student.timestamp,
          confidence: student.confidence
        })),
        absentStudents: absentStudents.map(student => ({
          studentId: student.id,
          reason: 'Not detected'
        })),
        attendancePercentage,
        totalStudents
      };
      
      console.log('Saving attendance data:', attendanceData);
      
      // Mock API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      addToast({ 
        message: 'Attendance saved successfully!', 
        type: 'success' 
      });
      
      // Navigate back to classroom
      setTimeout(() => {
        navigate(`/classroom/${code}`);
      }, 2000);
      
    } catch (error) {
      console.error('Error saving attendance:', error);
      addToast({ 
        message: 'Failed to save attendance. Please try again.', 
        type: 'error' 
      });
    }
  };
  
  const handleRetakeAttendance = () => {
    navigate(`/classroom/${code}/attendance`);
  };
  
  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      hour12: true
    });
  };
  
  const formatDate = (date: Date) => {
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  return (
    <div className="attendance-results-page">
      <div className="results-header">
        <button 
          className="back-button"
          onClick={() => navigate(`/classroom/${code}/attendance`)}
        >
          ← Back to Attendance
        </button>
        <div className="session-info">
          <h1>Attendance Results</h1>
          <div className="session-details">
            <span>Session: {session.sessionId}</span>
            <span>Date: {formatDate(session.startTime)}</span>
            <span>Time: {formatTime(session.startTime)}</span>
            <span>Duration: {session.timeSlot} minutes</span>
          </div>
        </div>
        <div className="summary-stats">
          <div className="stat-card attendance-rate">
            <div className="stat-value">{attendancePercentage.toFixed(1)}%</div>
            <div className="stat-label">Attendance Rate</div>
          </div>
          <div className="stat-card total-students">
            <div className="stat-value">{totalStudents}</div>
            <div className="stat-label">Total Students</div>
          </div>
        </div>
      </div>

      <div className="results-content">
        {/* Present Students Section */}
        <div className="attendance-section present-section">
          <div className="section-header">
            <h2>Present Students</h2>
            <div className="count-badge present-count">
              {presentStudents.length} Present
            </div>
          </div>
          
          <div className="students-container">
            {presentStudents.length > 0 ? (
              <div className="students-grid">
                {presentStudents.map((student) => (
                  <div key={student.studentId} className="student-card present">
                    <div className="student-avatar">
                      <img 
                        src={`/api/placeholder/60/60`}
                        alt={student.name}
                        onError={(e) => {
                          (e.target as HTMLImageElement).src = '/api/placeholder/60/60';
                        }}
                      />
                      <div className="status-badge present-badge">✓</div>
                    </div>
                    <div className="student-info">
                      <div className="student-name">{student.name}</div>
                      <div className="student-roll">{student.rollNumber}</div>
                      <div className="detection-details">
                        <div className="detection-time">
                          Detected at {formatTime(student.timestamp)}
                        </div>
                        <div className="confidence-score">
                          {(student.confidence * 100).toFixed(1)}% confidence
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="empty-state">
                <div className="empty-icon">👥</div>
                <div className="empty-message">No students detected</div>
                <div className="empty-description">
                  No students were detected during the facial recognition session.
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Absent Students Section */}
        <div className="attendance-section absent-section">
          <div className="section-header">
            <h2>Absent Students</h2>
            <div className="count-badge absent-count">
              {absentStudents.length} Absent
            </div>
          </div>
          
          <div className="students-container">
            {absentStudents.length > 0 ? (
              <div className="students-grid">
                {absentStudents.map((student) => (
                  <div key={student.id} className="student-card absent">
                    <div className="student-avatar">
                      <img 
                        src={student.profileImage || `/api/placeholder/60/60`}
                        alt={student.name}
                        onError={(e) => {
                          (e.target as HTMLImageElement).src = '/api/placeholder/60/60';
                        }}
                      />
                      <div className="status-badge absent-badge">✗</div>
                    </div>
                    <div className="student-info">
                      <div className="student-name">{student.name}</div>
                      <div className="student-roll">{student.rollNumber}</div>
                      <div className="absence-reason">
                        <div className="reason-text">Not detected during session</div>
                        <div className="reason-note">
                          May have joined late or camera couldn't detect face
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="empty-state">
                <div className="empty-icon">✅</div>
                <div className="empty-message">Perfect Attendance!</div>
                <div className="empty-description">
                  All registered students were detected and marked present.
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="results-actions">
        <button 
          className="action-btn secondary-btn"
          onClick={handleRetakeAttendance}
        >
          Retake Attendance
        </button>
        <button 
          className="action-btn primary-btn"
          onClick={handleSaveAttendance}
        >
          Save Attendance
        </button>
      </div>

      {/* Session Summary */}
      <div className="session-summary">
        <h3>Session Summary</h3>
        <div className="summary-grid">
          <div className="summary-item">
            <span className="summary-label">Session Duration:</span>
            <span className="summary-value">{session.timeSlot} minutes</span>
          </div>
          <div className="summary-item">
            <span className="summary-label">Detection Method:</span>
            <span className="summary-value">Facial Recognition</span>
          </div>
          <div className="summary-item">
            <span className="summary-label">Maximum Capacity:</span>
            <span className="summary-value">{session.maxStudents} students</span>
          </div>
          <div className="summary-item">
            <span className="summary-label">Session Started:</span>
            <span className="summary-value">{formatTime(session.startTime)}</span>
          </div>
          <div className="summary-item">
            <span className="summary-label">Total Registered:</span>
            <span className="summary-value">{totalStudents} students</span>
          </div>
          <div className="summary-item">
            <span className="summary-label">Attendance Rate:</span>
            <span className="summary-value">{attendancePercentage.toFixed(1)}%</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AttendanceResultsPage;