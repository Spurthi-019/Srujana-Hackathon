import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import { UserButton } from '@clerk/clerk-react';
import { useToast } from './contexts/ToastContext';
import ThemeToggle from './components/ThemeToggle';
import Breadcrumb from './components/Breadcrumb';
import './TakeNotesPage.css';

interface Subject {
  id: string;
  name: string;
  color: string;
  modules: Module[];
  assignedTeacher: string;
}

interface Module {
  id: string;
  name: string;
  topics: Topic[];
  progress: number;
}

interface Topic {
  id: string;
  name: string;
  description: string;
  scheduledDate?: string;
  pdfUrl?: string;
  completed: boolean;
}

interface DayNote {
  date: string;
  subject: string;
  topic: string;
  content: string;
  pdfUrl?: string;
  teacherNotes?: string;
}

const TakeNotesPage: React.FC = () => {
  const { code } = useParams<{ code: string }>();
  const { addToast } = useToast();
  
  const [selectedSubject, setSelectedSubject] = useState<string>('');
  const [selectedModule, setSelectedModule] = useState<string>('');
  const [currentDate, setCurrentDate] = useState(new Date());
  const [selectedDate, setSelectedDate] = useState<string>('');
  const [showPdfViewer, setShowPdfViewer] = useState(false);
  const [currentPdfUrl, setCurrentPdfUrl] = useState<string>('');
  
  // Sample data - in real app this would come from API
  const subjects: Subject[] = [
    {
      id: 'math',
      name: 'Mathematics',
      color: '#3b82f6',
      assignedTeacher: 'Dr. Sarah Johnson',
      modules: [
        {
          id: 'algebra',
          name: 'Algebra Basics',
          progress: 75,
          topics: [
            {
              id: 'linear-eq',
              name: 'Linear Equations',
              description: 'Understanding and solving linear equations',
              scheduledDate: '2025-09-13',
              pdfUrl: '/sample-notes/linear-equations.pdf',
              completed: true
            },
            {
              id: 'quadratic',
              name: 'Quadratic Equations',
              description: 'Solving quadratic equations using various methods',
              scheduledDate: '2025-09-15',
              pdfUrl: '/sample-notes/quadratic-equations.pdf',
              completed: false
            }
          ]
        },
        {
          id: 'geometry',
          name: 'Geometry Fundamentals',
          progress: 60,
          topics: [
            {
              id: 'triangles',
              name: 'Triangle Properties',
              description: 'Properties and theorems of triangles',
              scheduledDate: '2025-09-18',
              pdfUrl: '/sample-notes/triangles.pdf',
              completed: false
            }
          ]
        }
      ]
    },
    {
      id: 'physics',
      name: 'Physics',
      color: '#10b981',
      assignedTeacher: 'Prof. Michael Chen',
      modules: [
        {
          id: 'mechanics',
          name: 'Classical Mechanics',
          progress: 80,
          topics: [
            {
              id: 'motion',
              name: 'Laws of Motion',
              description: 'Newton\'s laws and their applications',
              scheduledDate: '2025-09-14',
              pdfUrl: '/sample-notes/laws-of-motion.pdf',
              completed: true
            }
          ]
        }
      ]
    },
    {
      id: 'chemistry',
      name: 'Chemistry',
      color: '#f59e0b',
      assignedTeacher: 'Dr. Emily Rodriguez',
      modules: [
        {
          id: 'organic',
          name: 'Organic Chemistry',
          progress: 45,
          topics: [
            {
              id: 'hydrocarbons',
              name: 'Hydrocarbons',
              description: 'Structure and properties of hydrocarbons',
              scheduledDate: '2025-09-16',
              pdfUrl: '/sample-notes/hydrocarbons.pdf',
              completed: false
            }
          ]
        }
      ]
    }
  ];

  const [dailyNotes] = useState<DayNote[]>([
    {
      date: '2025-09-13',
      subject: 'Mathematics',
      topic: 'Linear Equations',
      content: 'Covered basic linear equation solving methods',
      pdfUrl: '/sample-notes/linear-equations.pdf',
      teacherNotes: 'Students showed good understanding of the concept'
    },
    {
      date: '2025-09-14',
      subject: 'Physics',
      topic: 'Laws of Motion',
      content: 'Discussed Newton\'s three laws with practical examples',
      pdfUrl: '/sample-notes/laws-of-motion.pdf',
      teacherNotes: 'Need to focus more on third law applications'
    }
  ]);

  const getCurrentMonthCalendar = () => {
    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const startDate = new Date(firstDay);
    startDate.setDate(startDate.getDate() - firstDay.getDay());
    
    const calendar = [];
    const current = new Date(startDate);
    
    for (let week = 0; week < 6; week++) {
      const weekDays = [];
      for (let day = 0; day < 7; day++) {
        weekDays.push(new Date(current));
        current.setDate(current.getDate() + 1);
      }
      calendar.push(weekDays);
      if (current > lastDay && week >= 3) break;
    }
    
    return calendar;
  };

  const getDayNote = (date: Date): DayNote | undefined => {
    const dateStr = date.toISOString().split('T')[0];
    return dailyNotes.find(note => note.date === dateStr);
  };

  const getTopicForDate = (date: Date): Topic | undefined => {
    const dateStr = date.toISOString().split('T')[0];
    for (const subject of subjects) {
      for (const module of subject.modules) {
        for (const topic of module.topics) {
          if (topic.scheduledDate === dateStr) {
            return topic;
          }
        }
      }
    }
    return undefined;
  };

  const handleDateClick = (date: Date) => {
    const dateStr = date.toISOString().split('T')[0];
    setSelectedDate(dateStr);
    
    const dayNote = getDayNote(date);
    const topic = getTopicForDate(date);
    
    if (dayNote?.pdfUrl) {
      setCurrentPdfUrl(dayNote.pdfUrl);
      setShowPdfViewer(true);
      addToast({
        message: `Opening notes for ${dayNote.topic}`,
        type: 'info',
        duration: 3000
      });
    } else if (topic?.pdfUrl) {
      setCurrentPdfUrl(topic.pdfUrl);
      setShowPdfViewer(true);
      addToast({
        message: `Opening topic notes: ${topic.name}`,
        type: 'info',
        duration: 3000
      });
    } else {
      addToast({
        message: 'No notes available for this date',
        type: 'warning',
        duration: 3000
      });
    }
  };

  const selectedSubjectData = subjects.find(s => s.id === selectedSubject);
  const selectedModuleData = selectedSubjectData?.modules.find(m => m.id === selectedModule);

  console.log('Notes page code:', code);

  return (
    <div className="notes-page fade-in">
      <Breadcrumb />
      
      <div className="notes-header">
        <div className="notes-title-section">
          <h1>Class Notes & Planner</h1>
          <p>Organize your study materials and track daily lessons</p>
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

      <div className="notes-container">
        <div className="notes-sidebar">
          <div className="subjects-section">
            <h3>Subjects</h3>
            <div className="subjects-list">
              {subjects.map(subject => (
                <div
                  key={subject.id}
                  className={`subject-card ${selectedSubject === subject.id ? 'active' : ''} subject-${subject.id}`}
                  onClick={() => {
                    setSelectedSubject(subject.id);
                    setSelectedModule('');
                  }}
                >
                  <div className="subject-info">
                    <h4>{subject.name}</h4>
                    <p className="teacher-name">{subject.assignedTeacher}</p>
                    <div className="modules-count">
                      {subject.modules.length} modules
                    </div>
                  </div>
                  <div 
                    className={`subject-color-dot color-${subject.id}`}
                  />
                </div>
              ))}
            </div>
          </div>

          {selectedSubjectData && (
            <div className="modules-section">
              <h3>Modules</h3>
              <div className="modules-list">
                {selectedSubjectData.modules.map(module => (
                  <div
                    key={module.id}
                    className={`module-card ${selectedModule === module.id ? 'active' : ''}`}
                    onClick={() => setSelectedModule(module.id)}
                  >
                    <h4>{module.name}</h4>
                    <div className="module-progress">
                      <div className="progress-bar">
                        <div 
                          className="progress-fill" 
                          data-progress={module.progress}
                        />
                      </div>
                      <span>{module.progress}% complete</span>
                    </div>
                    <div className="topics-count">
                      {module.topics.length} topics
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {selectedModuleData && (
            <div className="topics-section">
              <h3>Topics</h3>
              <div className="topics-list">
                {selectedModuleData.topics.map(topic => (
                  <div
                    key={topic.id}
                    className={`topic-card ${topic.completed ? 'completed' : ''}`}
                    onClick={() => {
                      if (topic.pdfUrl) {
                        setCurrentPdfUrl(topic.pdfUrl);
                        setShowPdfViewer(true);
                      }
                    }}
                  >
                    <div className="topic-header">
                      <h5>{topic.name}</h5>
                      <div className={`topic-status ${topic.completed ? 'completed' : 'pending'}`}>
                        {topic.completed ? '✓' : '○'}
                      </div>
                    </div>
                    <p>{topic.description}</p>
                    {topic.scheduledDate && (
                      <div className="scheduled-date">
                        📅 {new Date(topic.scheduledDate).toLocaleDateString()}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        <div className="notes-main-content">
          <div className="calendar-section">
            <div className="calendar-header">
              <h2>
                {currentDate.toLocaleDateString('en-US', { 
                  month: 'long', 
                  year: 'numeric' 
                })}
              </h2>
              <div className="calendar-navigation">
                <button
                  className="nav-btn"
                  onClick={() => {
                    const newDate = new Date(currentDate);
                    newDate.setMonth(newDate.getMonth() - 1);
                    setCurrentDate(newDate);
                  }}
                >
                  ←
                </button>
                <button
                  className="nav-btn today-btn"
                  onClick={() => setCurrentDate(new Date())}
                >
                  Today
                </button>
                <button
                  className="nav-btn"
                  onClick={() => {
                    const newDate = new Date(currentDate);
                    newDate.setMonth(newDate.getMonth() + 1);
                    setCurrentDate(newDate);
                  }}
                >
                  →
                </button>
              </div>
            </div>

            <div className="calendar-grid">
              <div className="calendar-weekdays">
                {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(day => (
                  <div key={day} className="weekday">{day}</div>
                ))}
              </div>
              
              <div className="calendar-days">
                {getCurrentMonthCalendar().map((week, weekIndex) => (
                  <div key={weekIndex} className="calendar-week">
                    {week.map((date, dayIndex) => {
                      const dayNote = getDayNote(date);
                      const topic = getTopicForDate(date);
                      const isCurrentMonth = date.getMonth() === currentDate.getMonth();
                      const isToday = date.toDateString() === new Date().toDateString();
                      const hasContent = dayNote || topic;
                      
                      return (
                        <div
                          key={dayIndex}
                          className={`calendar-day ${
                            isCurrentMonth ? 'current-month' : 'other-month'
                          } ${isToday ? 'today' : ''} ${
                            hasContent ? 'has-content' : ''
                          } ${selectedDate === date.toISOString().split('T')[0] ? 'selected' : ''}`}
                          onClick={() => handleDateClick(date)}
                        >
                          <span className="day-number">{date.getDate()}</span>
                          {hasContent && (
                            <div className="day-indicator">
                              <div className="content-dot" />
                              <div className="day-preview">
                                {dayNote?.topic || topic?.name}
                              </div>
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                ))}
              </div>
            </div>
          </div>

          {selectedDate && (
            <div className="selected-day-details">
              <h3>Notes for {new Date(selectedDate).toLocaleDateString()}</h3>
              {(() => {
                const dayNote = dailyNotes.find(note => note.date === selectedDate);
                const topic = getTopicForDate(new Date(selectedDate));
                
                if (dayNote) {
                  return (
                    <div className="day-note-card">
                      <div className="note-header">
                        <h4>{dayNote.subject} - {dayNote.topic}</h4>
                        {dayNote.pdfUrl && (
                          <button
                            className="pdf-btn"
                            onClick={() => {
                              setCurrentPdfUrl(dayNote.pdfUrl!);
                              setShowPdfViewer(true);
                            }}
                          >
                            📄 View Notes
                          </button>
                        )}
                      </div>
                      <p className="note-content">{dayNote.content}</p>
                      {dayNote.teacherNotes && (
                        <div className="teacher-notes">
                          <strong>Teacher Notes:</strong>
                          <p>{dayNote.teacherNotes}</p>
                        </div>
                      )}
                    </div>
                  );
                } else if (topic) {
                  return (
                    <div className="topic-preview-card">
                      <div className="topic-header">
                        <h4>{topic.name}</h4>
                        {topic.pdfUrl && (
                          <button
                            className="pdf-btn"
                            onClick={() => {
                              setCurrentPdfUrl(topic.pdfUrl!);
                              setShowPdfViewer(true);
                            }}
                          >
                            📄 View Topic Notes
                          </button>
                        )}
                      </div>
                      <p>{topic.description}</p>
                      <div className={`topic-status ${topic.completed ? 'completed' : 'pending'}`}>
                        Status: {topic.completed ? 'Completed' : 'Scheduled'}
                      </div>
                    </div>
                  );
                } else {
                  return (
                    <div className="no-content">
                      <p>No notes or topics scheduled for this date.</p>
                      <button 
                        className="add-note-btn"
                        onClick={() => {
                          addToast({
                            message: 'Note creation feature coming soon!',
                            type: 'info',
                            duration: 3000
                          });
                        }}
                      >
                        + Add Note
                      </button>
                    </div>
                  );
                }
              })()}
            </div>
          )}
        </div>
      </div>

      {showPdfViewer && (
        <div className="pdf-viewer-overlay">
          <div className="pdf-viewer-container">
            <div className="pdf-viewer-header">
              <h3>Class Notes</h3>
              <button 
                className="close-btn"
                onClick={() => setShowPdfViewer(false)}
              >
                ✕
              </button>
            </div>
            <div className="pdf-viewer-content">
              {/* In a real app, you'd use a proper PDF viewer like react-pdf */}
              <div className="pdf-placeholder">
                <div className="pdf-icon">📄</div>
                <h3>PDF Notes Preview</h3>
                <p>File: {currentPdfUrl}</p>
                <p>This would display the actual PDF content using a PDF viewer library like react-pdf or PDF.js</p>
                <div className="pdf-actions">
                  <button className="download-btn">
                    📥 Download PDF
                  </button>
                  <button className="print-btn">
                    🖨️ Print
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TakeNotesPage;
