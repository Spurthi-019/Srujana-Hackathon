import React, { useCallback, useEffect, useRef, useState } from 'react';
import { useToast } from '../contexts/ToastContext';
import '../mouse-bg-effect.css';
import { geminiService } from '../services/geminiService';
import '../types/speechRecognition.d.ts';
import './ClassNotes.css';

interface TranscriptSegment {
  text: string;
  timestamp: Date;
  confidence: number;
  enhanced?: string; // Gemini-enhanced version
}

interface CalendarEvent {
  date: string;
  title: string;
  time: string;
  type: 'lecture' | 'assignment' | 'exam';
  pdfUrl?: string;
  pdfName?: string;
}

interface ClassDetails {
  id: string;
  className: string;
  subject: string;
  teacher: string;
  department: string;
  semester: string;
  credits: number;
  schedule: {
    days: string[];
    time: string;
    room: string;
  };
  totalStudents: number;
  currentSession: {
    topic: string;
    date: string;
    duration: string;
  };
}

const ClassNotes: React.FC = () => {
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
  
  const [activeView, setActiveView] = useState<'notes' | 'calendar'>('notes');
  const [currentDate, setCurrentDate] = useState(new Date());
  const [isRecording, setIsRecording] = useState(false);
  const [isViewingTranscript, setIsViewingTranscript] = useState(false);
  const [transcript, setTranscript] = useState<TranscriptSegment[]>([]);
  const [currentText, setCurrentText] = useState('');
  const [hasPermission, setHasPermission] = useState<boolean | null>(null);
  const [isEnhancing, setIsEnhancing] = useState(false);
  const [enhancedTranscript, setEnhancedTranscript] = useState<string>('');
  const [selectedEvent, setSelectedEvent] = useState<CalendarEvent | null>(null);
  const [showPdfViewer, setShowPdfViewer] = useState(false);
  
  const { addToast } = useToast();
  
  const recognitionRef = useRef<any | null>(null);
  
  // Auto-generate class details based on user
  const getClassDetails = (): ClassDetails => {
    const currentDate = new Date();
    
    // Generate random data pools
    const departments = [
      'Computer Science', 'Mathematics', 'Engineering', 'Physics', 'Chemistry',
      'Biology', 'Economics', 'Psychology', 'Business Administration', 'Literature',
      'History', 'Philosophy', 'Art & Design', 'Music', 'Political Science',
      'Environmental Science', 'Anthropology', 'Sociology', 'Linguistics', 'Archaeology'
    ];
    
    const classTypes = {
      'Computer Science': {
        subjects: [
          'Data Structures & Algorithms', 'Machine Learning', 'Database Systems', 
          'Web Development', 'Cybersecurity', 'Software Engineering', 'AI Ethics',
          'Cloud Computing', 'Mobile App Development', 'Computer Networks',
          'Blockchain Technology', 'Virtual Reality', 'Game Development', 'DevOps'
        ],
        classNames: [
          'Advanced Programming', 'AI Workshop', 'Database Lab', 'DevOps Practice',
          'Security Analysis', 'System Design', 'Ethics in Tech', 'Cloud Architecture',
          'Mobile Innovation', 'Network Programming', 'Crypto Systems', 'VR Development',
          'Gaming Studio', 'Deployment Automation'
        ],
        topics: [
          'Binary Search Trees', 'Neural Networks', 'Query Optimization', 
          'React Hooks', 'Encryption Algorithms', 'Design Patterns', 'Bias in AI',
          'Microservices', 'Flutter Development', 'TCP/IP Implementation',
          'Smart Contracts', 'Immersive Environments', 'Unity Engine', 'CI/CD Pipelines'
        ]
      },
      'Mathematics': {
        subjects: [
          'Calculus I', 'Linear Algebra', 'Statistics', 'Differential Equations',
          'Number Theory', 'Real Analysis', 'Discrete Mathematics', 'Topology',
          'Probability Theory', 'Abstract Algebra', 'Complex Analysis', 'Cryptography'
        ],
        classNames: [
          'Mathematical Analysis', 'Matrix Theory', 'Statistical Methods', 'ODE Solutions',
          'Prime Numbers', 'Real Functions', 'Combinatorics', 'Geometric Topology',
          'Random Variables', 'Group Theory', 'Complex Functions', 'Mathematical Cryptography'
        ],
        topics: [
          'Integration Techniques', 'Eigenvalues', 'Hypothesis Testing', 'Laplace Transforms',
          'Modular Arithmetic', 'Metric Spaces', 'Graph Theory', 'Fundamental Groups',
          'Central Limit Theorem', 'Ring Homomorphisms', 'Contour Integration', 'RSA Algorithm'
        ]
      },
      'Physics': {
        subjects: [
          'Classical Mechanics', 'Quantum Physics', 'Thermodynamics', 'Electromagnetism',
          'Optics', 'Nuclear Physics', 'Astrophysics', 'Solid State Physics',
          'Particle Physics', 'Relativity', 'Plasma Physics', 'Biophysics'
        ],
        classNames: [
          'Newtonian Dynamics', 'Quantum Mechanics', 'Heat & Energy', 'E&M Fields',
          'Wave Optics', 'Atomic Structure', 'Stellar Evolution', 'Crystal Physics',
          'Standard Model', 'Spacetime Physics', 'Plasma Dynamics', 'Biological Physics'
        ],
        topics: [
          'Conservation Laws', 'Wave Functions', 'Carnot Cycles', 'Maxwell Equations',
          'Interference Patterns', 'Radioactive Decay', 'Black Holes', 'Band Theory',
          'Feynman Diagrams', 'Time Dilation', 'Magnetohydrodynamics', 'Protein Folding'
        ]
      },
      'Art & Design': {
        subjects: [
          'Digital Art', 'Graphic Design', 'Photography', 'Sculpture',
          'Painting Techniques', 'Art History', 'Interior Design', 'Fashion Design',
          'Animation', 'Industrial Design', 'Typography', 'Color Theory'
        ],
        classNames: [
          'Digital Creation', 'Visual Communication', 'Visual Storytelling', 'Form & Space',
          'Brushwork Mastery', 'Cultural Aesthetics', 'Space Planning', 'Textile Innovation',
          'Motion Graphics', 'Product Design', 'Letter Forms', 'Chromatic Studies'
        ],
        topics: [
          'Photoshop Techniques', 'Brand Identity', 'Composition Rules', 'Welding Methods',
          'Oil Painting', 'Renaissance Art', 'Ergonomic Design', 'Sustainable Fashion',
          'Character Rigging', 'User Experience', 'Serif vs Sans-serif', 'Color Psychology'
        ]
      },
      'Psychology': {
        subjects: [
          'Cognitive Psychology', 'Social Psychology', 'Developmental Psychology', 'Abnormal Psychology',
          'Research Methods', 'Neuropsychology', 'Behavioral Analysis', 'Clinical Psychology',
          'Educational Psychology', 'Sports Psychology', 'Forensic Psychology', 'Health Psychology'
        ],
        classNames: [
          'Mind & Cognition', 'Group Dynamics', 'Human Development', 'Mental Health',
          'Scientific Method', 'Brain & Behavior', 'Learning Theory', 'Therapy Techniques',
          'Learning Psychology', 'Performance Enhancement', 'Criminal Behavior', 'Wellness Studies'
        ],
        topics: [
          'Memory Processes', 'Social Influence', 'Attachment Theory', 'Diagnostic Criteria',
          'Statistical Analysis', 'Brain Imaging', 'Conditioning', 'CBT Techniques',
          'Motivation Theory', 'Peak Performance', 'Profiling Methods', 'Stress Management'
        ]
      }
    };
    
    // Randomly select department
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    const randomDept = departments[Math.floor(Math.random() * departments.length)];
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    const deptData = classTypes[randomDept as keyof typeof classTypes] || classTypes['Computer Science'];
    
    // Generate random building names
    const buildings = ['Science', 'Engineering', 'Academic', 'Research', 'Innovation', 'Technology'];
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    const buildingName = buildings[Math.floor(Math.random() * buildings.length)];
    
    // Generate random room number
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    const roomNumber = Math.floor(Math.random() * 500) + 100;
    
    // Generate random schedule
    const schedulePatterns = [
      ['Monday', 'Wednesday', 'Friday'],
      ['Tuesday', 'Thursday'],
      ['Monday', 'Wednesday'],
      ['Tuesday', 'Friday'],
      ['Monday', 'Thursday']
    ];
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    const randomSchedule = schedulePatterns[Math.floor(Math.random() * schedulePatterns.length)];
    
    // Generate random time slots
    const timeSlots = [
      '8:00 AM - 9:30 AM', '9:00 AM - 10:30 AM', '10:00 AM - 11:30 AM',
      '11:00 AM - 12:30 PM', '1:00 PM - 2:30 PM', '2:00 PM - 3:30 PM',
      '3:00 PM - 4:30 PM', '4:00 PM - 5:30 PM'
    ];
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    const randomTime = timeSlots[Math.floor(Math.random() * timeSlots.length)];
    
    // Generate random course code
    const deptCode = randomDept.split(' ').map(word => word.charAt(0)).join('');
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    const courseId = `${deptCode}301-5`;
    
    // Select random data from department
    
    // Fixed class details for Kumar Ankit teaching DBMS
    return {
      id: 'CS301-5',
      className: 'Database Management Systems',
      subject: 'DBMS',
      teacher: 'Kumar Ankit',
      department: 'Computer Science',
      semester: 'Fall 2025',
      credits: 4,
      schedule: {
        days: ['Monday', 'Wednesday', 'Friday'],
        time: `${currentDate.toLocaleTimeString('en-US', { 
          hour: 'numeric', 
          minute: '2-digit',
          hour12: true 
        })} - ${new Date(currentDate.getTime() + 90 * 60000).toLocaleTimeString('en-US', { 
          hour: 'numeric', 
          minute: '2-digit',
          hour12: true 
        })}`,
        room: 'Tech Building - Room 201'
      },
      totalStudents: 45,
      currentSession: {
        topic: 'Advanced SQL Queries and Database Optimization',
        date: currentDate.toLocaleDateString('en-US', {
          weekday: 'long',
          year: 'numeric',
          month: 'long',
          day: 'numeric'
        }),
        duration: '90 minutes'
      }
    };
  };

  const [classDetails, setClassDetails] = useState<ClassDetails>(getClassDetails());
  
  // Function to regenerate random class details
  const regenerateClassDetails = () => {
    setClassDetails(getClassDetails());
    addToast({
      message: 'Class details refreshed with new random data!',
      type: 'success'
    });
  };
  
  // Mock calendar events - in real app, fetch from API
  const [calendarEvents] = useState<CalendarEvent[]>([
    { 
      date: '2025-09-15', 
      title: 'Math Lecture', 
      time: '10:00 AM', 
      type: 'lecture',
      pdfUrl: '/pdfs/math-lecture-week2.txt',
      pdfName: 'Math Lecture - Week 2.pdf'
    },
    { 
      date: '2025-09-16', 
      title: 'Physics Assignment Due', 
      time: '11:59 PM', 
      type: 'assignment',
      pdfUrl: '/pdfs/physics-assignment-3.txt',
      pdfName: 'Physics Assignment #3.pdf'
    },
    { 
      date: '2025-09-18', 
      title: 'Chemistry Lab', 
      time: '2:00 PM', 
      type: 'lecture',
      pdfUrl: '/pdfs/chemistry-lab-procedures.txt',
      pdfName: 'Chemistry Lab Procedures.pdf'
    },
    { 
      date: '2025-09-20', 
      title: 'Midterm Exam', 
      time: '9:00 AM', 
      type: 'exam',
      pdfUrl: '/pdfs/midterm-study-guide.txt',
      pdfName: 'Midterm Study Guide.pdf'
    },
  ]);

  // Calendar helper functions
  const getDaysInMonth = (date: Date) => {
    return new Date(date.getFullYear(), date.getMonth() + 1, 0).getDate();
  };

  const getFirstDayOfMonth = (date: Date) => {
    return new Date(date.getFullYear(), date.getMonth(), 1).getDay();
  };

  const formatDate = (date: Date) => {
    return date.toISOString().split('T')[0];
  };

  const getEventsForDate = (date: string) => {
    return calendarEvents.filter(event => event.date === date);
  };

  // PDF handling functions
  const downloadPDF = (event: CalendarEvent) => {
    if (event.pdfUrl && event.pdfName) {
      // Create a temporary link element to trigger download
      const link = document.createElement('a');
      link.href = event.pdfUrl;
      link.download = event.pdfName;
      link.target = '_blank';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      // Show toast notification
      addToast({
        message: `Downloading ${event.pdfName}`,
        type: 'success'
      });
    } else {
      addToast({
        message: 'No PDF available for this event',
        type: 'error'
      });
    }
  };

  const viewPDF = (event: CalendarEvent) => {
    if (event.pdfUrl) {
      setSelectedEvent(event);
      setShowPdfViewer(true);
    } else {
      addToast({
        message: 'No PDF available for this event',
        type: 'error'
      });
    }
  };

  const closePdfViewer = () => {
    setShowPdfViewer(false);
    setSelectedEvent(null);
  };

  const renderCalendar = () => {
    const daysInMonth = getDaysInMonth(currentDate);
    const firstDay = getFirstDayOfMonth(currentDate);
    const days = [];
    const monthNames = [
      'January', 'February', 'March', 'April', 'May', 'June',
      'July', 'August', 'September', 'October', 'November', 'December'
    ];

    // Empty cells for days before the first day of the month
    for (let i = 0; i < firstDay; i++) {
      days.push(<div key={`empty-${i}`} className="calendar-day empty"></div>);
    }

    // Days of the month
    for (let day = 1; day <= daysInMonth; day++) {
      const date = new Date(currentDate.getFullYear(), currentDate.getMonth(), day);
      const dateString = formatDate(date);
      const events = getEventsForDate(dateString);
      const isToday = dateString === formatDate(new Date());

      days.push(
        <div
          key={day}
          className={`calendar-day ${isToday ? 'today' : ''} ${events.length > 0 ? 'has-events' : ''}`}
        >
          <span className="day-number">{day}</span>
          {events.length > 0 && (
            <div className="event-indicators">
              {events.map((event, idx) => (
                <div
                  key={idx}
                  className={`event-dot ${event.type}`}
                  title={`${event.title} - ${event.time}`}
                ></div>
              ))}
            </div>
          )}
        </div>
      );
    }

    return (
      <div className="calendar-container">
        <div className="calendar-header">
          <button
            className="nav-btn"
            onClick={() => setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() - 1, 1))}
          >
            ‹
          </button>
          <h3>{monthNames[currentDate.getMonth()]} {currentDate.getFullYear()}</h3>
          <button
            className="nav-btn"
            onClick={() => setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 1))}
          >
            ›
          </button>
        </div>
        <div className="calendar-weekdays">
          {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(day => (
            <div key={day} className="weekday">{day}</div>
          ))}
        </div>
        <div className="calendar-grid">
          {days}
        </div>
        <div className="calendar-events">
          <h4>Upcoming Events</h4>
          {calendarEvents.slice(0, 3).map((event, idx) => (
            <div key={idx} className={`event-item ${event.type}`}>
              <div className="event-info">
                <span className="event-date">{new Date(event.date).toLocaleDateString()}</span>
                <span className="event-title">{event.title}</span>
                <span className="event-time">{event.time}</span>
              </div>
              {event.pdfUrl && (
                <div className="event-actions">
                  <button 
                    className="pdf-btn view-btn"
                    onClick={() => viewPDF(event)}
                    title="View PDF"
                  >
                    📄 View
                  </button>
                  <button 
                    className="pdf-btn download-btn"
                    onClick={() => downloadPDF(event)}
                    title="Download PDF"
                  >
                    📥 Download
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    );
  };

  // Speech Recognition Functions
  const requestMicrophonePermission = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      stream.getTracks().forEach(track => track.stop());
      setHasPermission(true);
    } catch (error) {
      console.error('Error requesting microphone permission:', error);
      setHasPermission(false);
    }
  }, []);

  // Initialize Speech Recognition
  useEffect(() => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      
      if (recognitionRef.current) {
        recognitionRef.current.continuous = true;
        recognitionRef.current.interimResults = true;
        recognitionRef.current.lang = 'en-US';
        recognitionRef.current.maxAlternatives = 1;

        recognitionRef.current.onresult = (event: any) => {
          let interimTranscript = '';

          for (let i = event.resultIndex; i < event.results.length; i++) {
            const result = event.results[i];
            if (result.isFinal) {
              setTranscript(prev => [...prev, {
                text: result[0].transcript,
                timestamp: new Date(),
                confidence: result[0].confidence
              }]);
            } else {
              interimTranscript += result[0].transcript;
            }
          }

          setCurrentText(interimTranscript);
        };

        recognitionRef.current.onerror = (event: any) => {
          console.error('Speech recognition error:', event.error);
        };

        recognitionRef.current.onend = () => {
          if (isRecording) {
            // Restart recognition if still recording
            try {
              recognitionRef.current?.start();
            } catch (error) {
              console.error('Error restarting recognition:', error);
            }
          }
        };
      }
    }

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
    };
  }, [isRecording]);

  // Check microphone permission
  useEffect(() => {
    const checkMicrophonePermission = async () => {
      try {
        const permission = await navigator.permissions.query({ name: 'microphone' as PermissionName });
        setHasPermission(permission.state === 'granted');
        
        permission.onchange = () => {
          setHasPermission(permission.state === 'granted');
        };
      } catch (error) {
        console.error('Error checking microphone permission:', error);
        setHasPermission(false);
      }
    };

    checkMicrophonePermission();
  }, []);

  // Start recording
  const startRecording = useCallback(async () => {
    if (!hasPermission) {
      await requestMicrophonePermission();
      return;
    }

    if (!recognitionRef.current) {
      console.error('Speech recognition not supported in this browser');
      return;
    }

    try {
      setIsRecording(true);
      setTranscript([]);
      setCurrentText('');
      recognitionRef.current.start();
    } catch (error) {
      console.error('Error starting recording:', error);
      setIsRecording(false);
    }
  }, [hasPermission, requestMicrophonePermission]);

  // Stop recording
  const stopRecording = useCallback(() => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }
    setIsRecording(false);
    setIsViewingTranscript(false);
  }, []);

  // Enhance transcript with Gemini AI
  const enhanceTranscript = useCallback(async () => {
    if (transcript.length === 0) return;
    
    setIsEnhancing(true);
    try {
      const fullText = transcript.map(segment => segment.text).join(' ');
      const enhanced = await geminiService.enhanceTranscript(fullText);
      setEnhancedTranscript(enhanced);
    } catch (error) {
      console.error('Error enhancing transcript:', error);
    } finally {
      setIsEnhancing(false);
    }
  }, [transcript]);

  // Download transcript as text file
  const downloadTranscript = useCallback(() => {
    const textToDownload = enhancedTranscript || transcript.map(segment => 
      `[${segment.timestamp.toLocaleTimeString()}] ${segment.text}`
    ).join('\n');
    
    const blob = new Blob([textToDownload], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `lecture-transcript-${new Date().toISOString().split('T')[0]}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  }, [transcript, enhancedTranscript]);

  return (
    <>
      <div className="mouse-bg-effect"></div>
      <div className="class-notes-page">
        {/* Navigation Header */}
        <div className="notes-header">
          <h2>📚 Class Notes & Recording</h2>
          <div className="view-selector">
            <button
              className={`view-btn ${activeView === 'notes' ? 'active' : ''}`}
              onClick={() => setActiveView('notes')}
            >
              🎙️ Record
            </button>
            <button
              className={`view-btn ${activeView === 'calendar' ? 'active' : ''}`}
              onClick={() => setActiveView('calendar')}
            >
              📅 Calendar
            </button>
          </div>
        </div>

        {/* Class Details Section */}
        <div className="class-details-section">
          <div className="class-info-header">
            <div className="header-left">
              <h3>📚 {classDetails.className}</h3>
              <span className="class-id">ID: {classDetails.id}</span>
            </div>
            <button 
              className="refresh-btn"
              onClick={regenerateClassDetails}
              title="Generate new random class details"
            >
              🔄 Randomize
            </button>
          </div>
          
          <div className="class-info-grid">
            <div className="info-card">
              <div className="info-label">Subject</div>
              <div className="info-value">{classDetails.subject}</div>
            </div>
            
            <div className="info-card">
              <div className="info-label">Instructor</div>
              <div className="info-value">{classDetails.teacher}</div>
            </div>
            
            <div className="info-card">
              <div className="info-label">Department</div>
              <div className="info-value">{classDetails.department}</div>
            </div>
            
            <div className="info-card">
              <div className="info-label">Semester</div>
              <div className="info-value">{classDetails.semester}</div>
            </div>
            
            <div className="info-card">
              <div className="info-label">Credits</div>
              <div className="info-value">{classDetails.credits}</div>
            </div>
            
            <div className="info-card">
              <div className="info-label">Schedule</div>
              <div className="info-value">
                {classDetails.schedule.days.join(', ')}<br/>
                <small>{classDetails.schedule.time}</small>
              </div>
            </div>
            
            <div className="info-card">
              <div className="info-label">Room</div>
              <div className="info-value">{classDetails.schedule.room}</div>
            </div>
            
            <div className="info-card">
              <div className="info-label">Students</div>
              <div className="info-value">{classDetails.totalStudents}</div>
            </div>
          </div>
          
          <div className="current-session">
            <h4>📖 Today's Session</h4>
            <div className="session-info">
              <div className="session-topic">
                <strong>Topic:</strong> {classDetails.currentSession.topic}
              </div>
              <div className="session-details">
                <span>📅 {classDetails.currentSession.date}</span>
                <span>⏰ {classDetails.currentSession.duration}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Content based on active view */}
        {activeView === 'notes' && (
          <div className="recorder-view fade-in">
            <div className="recorder-interface">
              <h3>🎙️ Lecture Recording</h3>
              
              {/* Simplified Recording Controls - Only 3 buttons */}
              <div className="recording-controls-simple">
                {!isRecording ? (
                  <button 
                    className="record-btn" 
                    onClick={startRecording}
                    disabled={hasPermission === false}
                  >
                    🎙️ Record Lecture
                  </button>
                ) : (
                  <div className="active-recording">
                    <div className="recording-status">
                      <div className="pulse-indicator"></div>
                      <span>Recording in progress...</span>
                    </div>
                    
                    <div className="recording-actions">
                      <button 
                        className="transcript-btn"
                        onClick={() => setIsViewingTranscript(!isViewingTranscript)}
                      >
                        📝 Watch Live Transcript
                      </button>
                      
                      <button 
                        className="stop-btn"
                        onClick={stopRecording}
                      >
                        ⏹️ Stop Recording
                      </button>
                    </div>
                  </div>
                )}
              </div>

              {/* Microphone Permission */}
              {hasPermission === false && (
                <div className="permission-warning">
                  <p>⚠️ Microphone access is required for recording. Please allow microphone permissions.</p>
                  <button onClick={requestMicrophonePermission} className="permission-btn">
                    Grant Permission
                  </button>
                </div>
              )}

              {/* Live Transcript View */}
              {isRecording && isViewingTranscript && (
                <div className="live-transcript">
                  <div className="transcript-header">
                    <h4>📝 Live Transcript</h4>
                    <div className="transcript-status">Real-time speech-to-text</div>
                  </div>
                  <div className="transcript-content">
                    <div className="transcript-text">
                      {transcript.map((segment, idx) => (
                        <div key={idx} className="transcript-segment">
                          <span className="timestamp">
                            {segment.timestamp.toLocaleTimeString()}
                          </span>
                          <span className="text">{segment.text}</span>
                        </div>
                      ))}
                      {currentText && (
                        <div className="transcript-segment interim">
                          <span className="timestamp">
                            {new Date().toLocaleTimeString()}
                          </span>
                          <span className="text">{currentText}</span>
                        </div>
                      )}
                      {transcript.length === 0 && !currentText && (
                        <div className="transcript-placeholder">
                          Start speaking to see live transcript...
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )}

              {/* Enhanced Transcript Section */}
              {transcript.length > 0 && !isRecording && (
                <div className="transcript-actions">
                  <h4>📄 Transcript Actions</h4>
                  <div className="action-buttons">
                    <button 
                      onClick={enhanceTranscript}
                      disabled={isEnhancing}
                      className="enhance-btn"
                    >
                      {isEnhancing ? '🔄 Enhancing...' : '✨ Enhance with AI'}
                    </button>
                    <button 
                      onClick={downloadTranscript}
                      className="download-btn"
                    >
                      💾 Download Transcript
                    </button>
                  </div>
                  
                  {enhancedTranscript && (
                    <div className="enhanced-transcript">
                      <h5>✨ AI Enhanced Transcript:</h5>
                      <div className="enhanced-content">
                        {enhancedTranscript}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        )}

        {activeView === 'calendar' && (
          <div className="calendar-view fade-in">
            {renderCalendar()}
          </div>
        )}
      </div>

      {/* PDF Viewer Modal */}
      {showPdfViewer && selectedEvent && (
        <div className="pdf-viewer-modal" onClick={closePdfViewer}>
          <div className="pdf-viewer-content" onClick={(e) => e.stopPropagation()}>
            <div className="pdf-viewer-header">
              <h3>📄 {selectedEvent.pdfName || selectedEvent.title}</h3>
              <div className="pdf-viewer-actions">
                <button 
                  className="pdf-btn download-btn"
                  onClick={() => downloadPDF(selectedEvent)}
                >
                  📥 Download
                </button>
                <button 
                  className="close-btn"
                  onClick={closePdfViewer}
                >
                  ✕
                </button>
              </div>
            </div>
            <div className="pdf-viewer-body">
              <iframe
                src={selectedEvent.pdfUrl}
                width="100%"
                height="100%"
                title={selectedEvent.pdfName || selectedEvent.title}
              />
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default ClassNotes;
