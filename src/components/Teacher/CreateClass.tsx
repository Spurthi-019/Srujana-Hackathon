import { useUser } from '@clerk/clerk-react';
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiService } from '../../services/api';
import './CreateClass.css';
import './SchedulePlanner.css';

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

const CreateClass: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useUser();
  const [currentStep, setCurrentStep] = useState<'basic' | 'files' | 'schedule'>('basic');
  const [formData, setFormData] = useState<ClassFormData>({
    className: '',
    classLevel: '',
    subject: '',
    semester: '',
    department: '',
    syllabus: null,
    notes: null
  });
  
  const [schedule, setSchedule] = useState<ScheduleEntry[]>([]);
  const [currentMonth, setCurrentMonth] = useState(new Date().getMonth());
  const [currentYear, setCurrentYear] = useState(new Date().getFullYear());

  const classLevels = ['1st Year', '2nd Year', '3rd Year', '4th Year'];
  const semesters = ['1st Semester', '2nd Semester', '3rd Semester', '4th Semester', '5th Semester', '6th Semester', '7th Semester', '8th Semester'];
  const departments = ['Computer Science', 'Information Technology', 'Electronics', 'Mechanical', 'Civil', 'Electrical'];
  const subjects = ['Programming', 'Data Structures', 'Algorithms', 'Database Systems', 'Web Development', 'Machine Learning', 'Computer Networks', 'Software Engineering'];

  const monthNames = ['January', 'February', 'March', 'April', 'May', 'June', 
                     'July', 'August', 'September', 'October', 'November', 'December'];

  const handleInputChange = (field: keyof ClassFormData, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleFileChange = (field: 'syllabus' | 'notes', file: File | null) => {
    setFormData(prev => ({
      ...prev,
      [field]: file
    }));
  };

  const getDaysInMonth = (month: number, year: number) => {
    return new Date(year, month + 1, 0).getDate();
  };

  const getFirstDayOfMonth = (month: number, year: number) => {
    return new Date(year, month, 1).getDay();
  };

  const addScheduleEntry = (day: number) => {
    const dateString = `${currentYear}-${String(currentMonth + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
    const existingEntry = schedule.find(entry => entry.day === dateString);
    
    if (!existingEntry) {
      setSchedule(prev => [...prev, {
        day: dateString,
        topic: '',
        materials: null,
        notes: ''
      }]);
    }
  };

  const updateScheduleEntry = (day: string, field: keyof ScheduleEntry, value: string | File | null) => {
    setSchedule(prev => prev.map(entry => 
      entry.day === day ? { ...entry, [field]: value } : entry
    ));
  };

  const removeScheduleEntry = (day: string) => {
    setSchedule(prev => prev.filter(entry => entry.day !== day));
  };

  const renderCalendar = () => {
    const daysInMonth = getDaysInMonth(currentMonth, currentYear);
    const firstDay = getFirstDayOfMonth(currentMonth, currentYear);
    const days = [];

    // Empty cells for days before the first day of the month
    for (let i = 0; i < firstDay; i++) {
      days.push(<div key={`empty-${i}`} className="calendar-day empty"></div>);
    }

    // Days of the month
    for (let day = 1; day <= daysInMonth; day++) {
      const dateString = `${currentYear}-${String(currentMonth + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
      const hasSchedule = schedule.some(entry => entry.day === dateString);
      
      days.push(
        <div 
          key={day} 
          className={`calendar-day ${hasSchedule ? 'has-schedule' : ''}`}
          onClick={() => addScheduleEntry(day)}
        >
          <span className="day-number">{day}</span>
          {hasSchedule && <span className="schedule-indicator">📚</span>}
        </div>
      );
    }

    return days;
  };

  const renderBasicInfo = () => (
    <div className="form-section">
      <h3>Basic Class Information</h3>
      <div className="form-grid">
        <div className="form-group">
          <label>Class Name</label>
          <input
            type="text"
            value={formData.className}
            onChange={(e) => handleInputChange('className', e.target.value)}
            placeholder="Enter class name"
            className="form-input"
          />
        </div>

        <div className="form-group">
          <label>Class Level</label>
          <select
            value={formData.classLevel}
            onChange={(e) => handleInputChange('classLevel', e.target.value)}
            className="form-select"
          >
            <option value="">Select class level</option>
            {classLevels.map(level => (
              <option key={level} value={level}>{level}</option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label>Subject</label>
          <select
            value={formData.subject}
            onChange={(e) => handleInputChange('subject', e.target.value)}
            className="form-select"
          >
            <option value="">Select subject</option>
            {subjects.map(subject => (
              <option key={subject} value={subject}>{subject}</option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label>Semester</label>
          <select
            value={formData.semester}
            onChange={(e) => handleInputChange('semester', e.target.value)}
            className="form-select"
          >
            <option value="">Select semester</option>
            {semesters.map(semester => (
              <option key={semester} value={semester}>{semester}</option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label>Department</label>
          <select
            value={formData.department}
            onChange={(e) => handleInputChange('department', e.target.value)}
            className="form-select"
          >
            <option value="">Select department</option>
            {departments.map(dept => (
              <option key={dept} value={dept}>{dept}</option>
            ))}
          </select>
        </div>
      </div>
    </div>
  );

  const renderFileUploads = () => (
    <div className="form-section">
      <h3>Course Materials</h3>
      <div className="upload-grid">
        <div className="upload-group">
          <label>Upload Syllabus</label>
          <div className="file-upload-area">
            <input
              type="file"
              accept=".pdf,.doc,.docx"
              onChange={(e) => handleFileChange('syllabus', e.target.files?.[0] || null)}
              className="file-input"
              id="syllabus-upload"
            />
            <label htmlFor="syllabus-upload" className="file-upload-label">
              <span className="upload-icon">📄</span>
              <span className="upload-text">
                {formData.syllabus ? formData.syllabus.name : 'Click to upload syllabus'}
              </span>
            </label>
          </div>
          <p className="upload-hint">Supported formats: PDF, DOC, DOCX</p>
        </div>

        <div className="upload-group">
          <label>Upload Course Notes</label>
          <div className="file-upload-area">
            <input
              type="file"
              accept=".pdf,.doc,.docx,.ppt,.pptx"
              onChange={(e) => handleFileChange('notes', e.target.files?.[0] || null)}
              className="file-input"
              id="notes-upload"
            />
            <label htmlFor="notes-upload" className="file-upload-label">
              <span className="upload-icon">📚</span>
              <span className="upload-text">
                {formData.notes ? formData.notes.name : 'Click to upload course notes'}
              </span>
            </label>
          </div>
          <p className="upload-hint">Supported formats: PDF, DOC, DOCX, PPT, PPTX</p>
        </div>
      </div>
    </div>
  );

  const renderSchedulePlanner = () => (
    <div className="form-section">
      <h3>Create Daily Schedule</h3>
      <div className="schedule-planner">
        <div className="calendar-header">
          <button 
            className="nav-btn"
            onClick={() => {
              if (currentMonth === 0) {
                setCurrentMonth(11);
                setCurrentYear(currentYear - 1);
              } else {
                setCurrentMonth(currentMonth - 1);
              }
            }}
          >
            ←
          </button>
          <h4>{monthNames[currentMonth]} {currentYear}</h4>
          <button 
            className="nav-btn"
            onClick={() => {
              if (currentMonth === 11) {
                setCurrentMonth(0);
                setCurrentYear(currentYear + 1);
              } else {
                setCurrentMonth(currentMonth + 1);
              }
            }}
          >
            →
          </button>
        </div>

        <div className="calendar-grid">
          <div className="calendar-weekdays">
            {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(day => (
              <div key={day} className="weekday">{day}</div>
            ))}
          </div>
          <div className="calendar-days">
            {renderCalendar()}
          </div>
        </div>

        <div className="schedule-entries">
          <h4>Scheduled Topics</h4>
          {schedule.length === 0 ? (
            <p className="no-schedule">Click on calendar days to add topics</p>
          ) : (
            <div className="schedule-list">
              {schedule.map(entry => {
                const date = new Date(entry.day);
                const formattedDate = date.toLocaleDateString('en-US', { 
                  month: 'short', 
                  day: 'numeric',
                  year: 'numeric'
                });
                
                return (
                  <div key={entry.day} className="schedule-entry">
                    <div className="entry-header">
                      <span className="entry-date">{formattedDate}</span>
                      <button 
                        className="remove-btn"
                        onClick={() => removeScheduleEntry(entry.day)}
                      >
                        ✕
                      </button>
                    </div>
                    <div className="entry-content">
                      <input
                        type="text"
                        placeholder="Topic to be taught"
                        value={entry.topic}
                        onChange={(e) => updateScheduleEntry(entry.day, 'topic', e.target.value)}
                        className="topic-input"
                      />
                      <textarea
                        placeholder="Additional notes"
                        value={entry.notes}
                        onChange={(e) => updateScheduleEntry(entry.day, 'notes', e.target.value)}
                        className="notes-input"
                        rows={2}
                      />
                      <div className="material-upload">
                        <input
                          type="file"
                          accept=".pdf,.doc,.docx,.ppt,.pptx"
                          onChange={(e) => updateScheduleEntry(entry.day, 'materials', e.target.files?.[0] || null)}
                          className="file-input"
                          id={`material-${entry.day}`}
                        />
                        <label htmlFor={`material-${entry.day}`} className="material-upload-label">
                          📎 {entry.materials ? entry.materials.name : 'Upload material for this day'}
                        </label>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );

  const canProceedToNext = () => {
    switch (currentStep) {
      case 'basic':
        return formData.className && formData.classLevel && formData.subject && 
               formData.semester && formData.department;
      case 'files':
        return formData.syllabus && formData.notes;
      case 'schedule':
        return schedule.length > 0 && schedule.every(entry => entry.topic.trim() !== '');
      default:
        return false;
    }
  };

  const handleNext = () => {
    if (currentStep === 'basic') {
      setCurrentStep('files');
    } else if (currentStep === 'files') {
      setCurrentStep('schedule');
    }
  };

  const handleBack = () => {
    if (currentStep === 'files') {
      setCurrentStep('basic');
    } else if (currentStep === 'schedule') {
      setCurrentStep('files');
    }
  };

  const handleSubmit = async () => {
    if (!user) {
      alert('User not authenticated');
      return;
    }

    try {
      // Get teacher information from Clerk user
      const userEmail = user.emailAddresses[0]?.emailAddress || '';
      
      if (!userEmail) {
        alert('Please complete your profile information');
        return;
      }

      // Use a default college name or get from form data
      const collegeName = "Default College"; // You may want to add this to form data
      
      // Generate class ID based on our format
      const departmentCode = formData.department.substring(0, 2).toUpperCase();
      const classroomId = `${collegeName.replace(/\s+/g, '')}_${departmentCode}_${formData.classLevel.replace(/\s+/g, '')}_${user.id}`;
      
      // Create class using backend API
      const classData = {
        classroom_id: classroomId,
        teacher_clerk_id: user.id,
        college_name: collegeName,
        subject: formData.subject,
        max_students: 60 // Default value
      };

      const response = await apiService.createClass(classData) as any;
      
      if (response.success) {
        // Navigate to confirmation page with data
        navigate('/teacher/class-confirmation', { 
          state: { 
            formData, 
            schedule, 
            classCode: classroomId,
            response
          } 
        });
      } else {
        alert('Failed to create class: ' + (response.error || 'Unknown error'));
      }
    } catch (error: any) {
      alert('Error creating class: ' + error.message);
    }
  };

  const renderStepContent = () => {
    switch (currentStep) {
      case 'basic':
        return renderBasicInfo();
      case 'files':
        return renderFileUploads();
      case 'schedule':
        return renderSchedulePlanner();
      default:
        return renderBasicInfo();
    }
  };

  return (
    <div className="create-class">
      <div className="create-class-header">
        <button className="back-btn" onClick={() => navigate('/teacher/dashboard')}>
          ← Back to Dashboard
        </button>
        <h1>Create New Class</h1>
      </div>

      <div className="progress-bar">
        <div className={`progress-step ${currentStep === 'basic' ? 'active' : (currentStep === 'files' || currentStep === 'schedule') ? 'completed' : ''}`}>
          <div className="step-number">1</div>
          <span>Basic Info</span>
        </div>
        <div className={`progress-step ${currentStep === 'files' ? 'active' : currentStep === 'schedule' ? 'completed' : ''}`}>
          <div className="step-number">2</div>
          <span>Upload Files</span>
        </div>
        <div className={`progress-step ${currentStep === 'schedule' ? 'active' : ''}`}>
          <div className="step-number">3</div>
          <span>Create Schedule</span>
        </div>
      </div>

      <div className="form-container">
        {renderStepContent()}
      </div>

      <div className="form-actions">
        {currentStep !== 'basic' && (
          <button className="back-button" onClick={handleBack}>
            Previous
          </button>
        )}
        
        {currentStep !== 'schedule' ? (
          <button 
            className="next-button" 
            onClick={handleNext}
            disabled={!canProceedToNext()}
          >
            Next
          </button>
        ) : (
          <button 
            className="submit-button" 
            onClick={handleSubmit}
            disabled={!canProceedToNext()}
          >
            Create Class
          </button>
        )}
      </div>
    </div>
  );
};

export default CreateClass;