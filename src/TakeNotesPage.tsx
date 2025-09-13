import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import { UserButton } from '@clerk/clerk-react';
import { useToast } from './contexts/ToastContext';
import ThemeToggle from './components/ThemeToggle';
import Breadcrumb from './components/Breadcrumb';
import LectureRecorder from './components/LectureRecorder';
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
  const [showRecorder, setShowRecorder] = useState(false);
  const [, setRecordedLectures] = useState<string[]>([]);
  const [showInstructions, setShowInstructions] = useState(true);
  
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

  // Subject icons mapping
  const subjectIcons = {
    math: '📐',
    physics: '⚡',
    chemistry: '🧪'
  };

  // Get module icon based on name
  const getModuleIcon = (moduleName: string) => {
    if (moduleName.toLowerCase().includes('algebra')) return '🔢';
    if (moduleName.toLowerCase().includes('geometry')) return '📐';
    if (moduleName.toLowerCase().includes('mechanics')) return '⚙️';
    if (moduleName.toLowerCase().includes('organic')) return '🧬';
    return '📚';
  };

  // Get topic difficulty indicator
  const getTopicDifficulty = (topicName: string) => {
    if (topicName.toLowerCase().includes('basic') || topicName.toLowerCase().includes('fundamental')) return { icon: '🟢', level: 'Easy' };
    if (topicName.toLowerCase().includes('advanced') || topicName.toLowerCase().includes('complex')) return { icon: '🔴', level: 'Hard' };
    return { icon: '🟡', level: 'Medium' };
  };

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

  // Handle recording completion
  const handleRecordingComplete = (pdfUrl: string) => {
    setRecordedLectures(prev => [...prev, pdfUrl]);
    setCurrentPdfUrl(pdfUrl);
    setShowPdfViewer(true);
    setShowRecorder(false);
    
    addToast({
      message: 'Lecture recording completed and saved as PDF!',
      type: 'success',
      duration: 5000
    });
  };

  // Start recording for current context
  const startLectureRecording = () => {
    if (!selectedSubjectData) {
      addToast({
        message: 'Please select a subject first',
        type: 'warning',
        duration: 3000
      });
      return;
    }

    const currentTopic = selectedModuleData?.topics.find(t => 
      t.scheduledDate === new Date().toISOString().split('T')[0]
    ) || selectedModuleData?.topics[0];

    if (!currentTopic) {
      addToast({
        message: 'No topic available for recording',
        type: 'warning',
        duration: 3000
      });
      return;
    }

    setShowRecorder(true);
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
          <button 
            className="record-lecture-btn"
            onClick={startLectureRecording}
            disabled={!selectedSubjectData}
          >
            🎙️ Record Lecture
          </button>
          {!showInstructions && (
            <button 
              className="show-instructions-btn"
              onClick={() => setShowInstructions(true)}
            >
              ❓ Instructions
            </button>
          )}
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

      {showInstructions && (
        <div className="recording-instructions">
          <div className="instructions-header">
            <h3>🎙️ How to Use Lecture Recording</h3>
            <button 
              className="close-instructions-btn"
              onClick={() => setShowInstructions(false)}
            >
              ✕
            </button>
          </div>
          <div className="instructions-content">
            <div className="instructions-steps">
              <div className="instruction-step">
                <span className="step-number">1</span>
                <div className="step-content">
                  <h4>Select a Subject</h4>
                  <p>Choose Math, Physics, or Chemistry from the sidebar</p>
                </div>
              </div>
              <div className="instruction-step">
                <span className="step-number">2</span>
                <div className="step-content">
                  <h4>Click "🎙️ Record Lecture"</h4>
                  <p>Find the recording button in the header above</p>
                </div>
              </div>
              <div className="instruction-step">
                <span className="step-number">3</span>
                <div className="step-content">
                  <h4>Grant Microphone Permission</h4>
                  <p>Allow browser access to your microphone when prompted</p>
                </div>
              </div>
              <div className="instruction-step">
                <span className="step-number">4</span>
                <div className="step-content">
                  <h4>Start Recording & Speak Clearly</h4>
                  <p>Click start and speak normally into your microphone</p>
                </div>
              </div>
              <div className="instruction-step">
                <span className="step-number">5</span>
                <div className="step-content">
                  <h4>Watch Live Transcription</h4>
                  <p>See your speech converted to text in real-time</p>
                </div>
              </div>
              <div className="instruction-step">
                <span className="step-number">6</span>
                <div className="step-content">
                  <h4>Stop Recording for PDF</h4>
                  <p>Click stop to generate and download your lecture notes</p>
                </div>
              </div>
            </div>
            <div className="instructions-features">
              <h4>✨ Features:</h4>
              <ul>
                <li>🔤 <strong>Real-time Speech-to-Text</strong> - See transcription as you speak</li>
                <li>📝 <strong>Grammar Correction</strong> - Automatic text improvement</li>
                <li>📄 <strong>PDF Generation</strong> - Professional lecture notes with metadata</li>
                <li>⏸️ <strong>Pause/Resume</strong> - Control recording as needed</li>
                <li>📊 <strong>Subject Context</strong> - Notes linked to specific subjects/topics</li>
              </ul>
            </div>
          </div>
        </div>
      )}

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
                  <div className="subject-icon">
                    {subjectIcons[subject.id as keyof typeof subjectIcons]}
                  </div>
                  <div className="subject-info">
                    <h4>{subject.name}</h4>
                    <p className="teacher-name">👩‍🏫 {subject.assignedTeacher}</p>
                    <div className="modules-count">
                      📚 {subject.modules.length} modules
                    </div>
                    <div className="subject-stats">
                      <span className="total-topics">
                        📝 {subject.modules.reduce((acc, mod) => acc + mod.topics.length, 0)} topics
                      </span>
                      <span className="avg-progress">
                        📊 {Math.round(subject.modules.reduce((acc, mod) => acc + mod.progress, 0) / subject.modules.length)}% avg
                      </span>
                    </div>
                  </div>
                  <div className="subject-action">
                    <span className="select-indicator">→</span>
                  </div>
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
                    <div className="module-header">
                      <span className="module-icon">{getModuleIcon(module.name)}</span>
                      <h4>{module.name}</h4>
                      <div className="module-status">
                        {module.progress === 100 ? '✅' : module.progress > 0 ? '⏳' : '📋'}
                      </div>
                    </div>
                    <div className="module-progress">
                      <div className="progress-bar">
                        <div 
                          className="progress-fill" 
                          data-progress={module.progress}
                        />
                      </div>
                      <span>📈 {module.progress}% complete</span>
                    </div>
                    <div className="module-stats">
                      <span className="topics-count">
                        📝 {module.topics.length} topics
                      </span>
                      <span className="completed-topics">
                        ✅ {module.topics.filter(t => t.completed).length} done
                      </span>
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
                {selectedModuleData.topics.map(topic => {
                  const difficulty = getTopicDifficulty(topic.name);
                  return (
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
                        <div className="topic-title">
                          <span className="topic-icon">📄</span>
                          <h5>{topic.name}</h5>
                        </div>
                        <div className="topic-indicators">
                          <span 
                            className="difficulty-indicator" 
                            title={`Difficulty: ${difficulty.level}`}
                          >
                            {difficulty.icon}
                          </span>
                          <div className={`topic-status ${topic.completed ? 'completed' : 'pending'}`}>
                            {topic.completed ? '✅' : '🔄'}
                          </div>
                        </div>
                      </div>
                      <p>{topic.description}</p>
                      <div className="topic-footer">
                        {topic.scheduledDate && (
                          <div className="scheduled-date">
                            📅 {new Date(topic.scheduledDate).toLocaleDateString()}
                          </div>
                        )}
                        {topic.pdfUrl && (
                          <div className="has-pdf">
                            📄 PDF Available
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>

        <div className="notes-main-content">
          <div className="calendar-section">
            <div className="calendar-header">
              <div className="calendar-title">
                <span className="calendar-icon">📅</span>
                <h2>
                  {currentDate.toLocaleDateString('en-US', { 
                    month: 'long', 
                    year: 'numeric' 
                  })}
                </h2>
              </div>
              <div className="calendar-navigation">
                <button
                  className="nav-btn prev-btn"
                  onClick={() => {
                    const newDate = new Date(currentDate);
                    newDate.setMonth(newDate.getMonth() - 1);
                    setCurrentDate(newDate);
                  }}
                  title="Previous Month"
                >
                  ⬅️
                </button>
                <button
                  className="nav-btn today-btn"
                  onClick={() => setCurrentDate(new Date())}
                  title="Go to Today"
                >
                  🏠 Today
                </button>
                <button
                  className="nav-btn next-btn"
                  onClick={() => {
                    const newDate = new Date(currentDate);
                    newDate.setMonth(newDate.getMonth() + 1);
                    setCurrentDate(newDate);
                  }}
                  title="Next Month"
                >
                  ➡️
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
                          title={hasContent ? `Click to view: ${dayNote?.topic || topic?.name}` : 'No content for this date'}
                        >
                          <span className="day-number">{date.getDate()}</span>
                          {hasContent && (
                            <div className="day-indicator">
                              <div className="content-icons">
                                {dayNote && <span className="note-icon" title="Daily Notes">📝</span>}
                                {topic && <span className="topic-icon" title="Scheduled Topic">📚</span>}
                                {(dayNote?.pdfUrl || topic?.pdfUrl) && <span className="pdf-icon" title="PDF Available">📄</span>}
                              </div>
                              <div className="day-preview">
                                {dayNote?.topic || topic?.name}
                              </div>
                            </div>
                          )}
                          {isToday && (
                            <div className="today-indicator">
                              <span>📍</span>
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
              <div className="day-details-header">
                <h3>📋 Notes for {new Date(selectedDate).toLocaleDateString()}</h3>
                <div className="day-actions">
                  <button 
                    className="quick-action-btn"
                    onClick={() => {
                      addToast({
                        message: 'Quick add feature coming soon!',
                        type: 'info',
                        duration: 3000
                      });
                    }}
                    title="Quick Add Note"
                  >
                    ➕ Add
                  </button>
                  <button 
                    className="quick-action-btn"
                    onClick={() => setSelectedDate('')}
                    title="Close Details"
                  >
                    ✕ Close
                  </button>
                </div>
              </div>
              {(() => {
                const dayNote = dailyNotes.find(note => note.date === selectedDate);
                const topic = getTopicForDate(new Date(selectedDate));
                
                if (dayNote) {
                  return (
                    <div className="day-note-card">
                      <div className="note-header">
                        <div className="note-title">
                          <span className="note-type-icon">📝</span>
                          <h4>{dayNote.subject} - {dayNote.topic}</h4>
                        </div>
                        {dayNote.pdfUrl && (
                          <button
                            className="pdf-btn"
                            onClick={() => {
                              setCurrentPdfUrl(dayNote.pdfUrl!);
                              setShowPdfViewer(true);
                            }}
                            title="View PDF Notes"
                          >
                            📄 View Notes
                          </button>
                        )}
                      </div>
                      <div className="note-content-section">
                        <div className="content-label">📖 Lecture Content:</div>
                        <p className="note-content">{dayNote.content}</p>
                      </div>
                      {dayNote.teacherNotes && (
                        <div className="teacher-notes">
                          <div className="teacher-notes-header">
                            <span className="teacher-icon">👩‍🏫</span>
                            <strong>Teacher Feedback:</strong>
                          </div>
                          <p>{dayNote.teacherNotes}</p>
                        </div>
                      )}
                    </div>
                  );
                } else if (topic) {
                  return (
                    <div className="topic-preview-card">
                      <div className="topic-header">
                        <div className="topic-title">
                          <span className="topic-type-icon">📚</span>
                          <h4>{topic.name}</h4>
                        </div>
                        {topic.pdfUrl && (
                          <button
                            className="pdf-btn"
                            onClick={() => {
                              setCurrentPdfUrl(topic.pdfUrl!);
                              setShowPdfViewer(true);
                            }}
                            title="View Topic Materials"
                          >
                            📄 View Materials
                          </button>
                        )}
                      </div>
                      <div className="topic-description">
                        <span className="description-icon">📋</span>
                        <p>{topic.description}</p>
                      </div>
                      <div className="topic-status-section">
                        <div className={`topic-status ${topic.completed ? 'completed' : 'pending'}`}>
                          <span className="status-icon">{topic.completed ? '✅' : '⏳'}</span>
                          <span>Status: {topic.completed ? 'Completed' : 'Scheduled'}</span>
                        </div>
                      </div>
                    </div>
                  );
                } else {
                  return (
                    <div className="no-content">
                      <div className="no-content-icon">📝</div>
                      <p>No notes or topics scheduled for this date.</p>
                      <div className="no-content-actions">
                        <button 
                          className="add-note-btn"
                          onClick={() => {
                            addToast({
                              message: 'Note creation feature coming soon!',
                              type: 'info',
                              duration: 3000
                            });
                          }}
                          title="Create New Note"
                        >
                          ➕ Add Note
                        </button>
                        <button 
                          className="schedule-topic-btn"
                          onClick={() => {
                            addToast({
                              message: 'Topic scheduling feature coming soon!',
                              type: 'info',
                              duration: 3000
                            });
                          }}
                          title="Schedule Topic"
                        >
                          📅 Schedule Topic
                        </button>
                      </div>
                    </div>
                  );
                }
              })()}
            </div>
          )}
        </div>
      </div>

      {showRecorder && selectedSubjectData && (
        <div className="recorder-container">
          <div className="recorder-header-controls">
            <h3>🎙️ Recording Session</h3>
            <button 
              className="close-recorder-btn"
              onClick={() => setShowRecorder(false)}
            >
              ✕ Close
            </button>
          </div>
          <LectureRecorder
            subject={selectedSubjectData.name}
            topic={selectedModuleData?.topics.find(t => 
              t.scheduledDate === new Date().toISOString().split('T')[0]
            )?.name || selectedModuleData?.topics[0]?.name || 'General Lecture'}
            date={new Date().toISOString().split('T')[0]}
            teacherName={selectedSubjectData.assignedTeacher}
            onRecordingComplete={handleRecordingComplete}
          />
        </div>
      )}

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
