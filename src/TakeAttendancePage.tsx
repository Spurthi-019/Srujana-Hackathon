import React, { useState, useRef, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useToast } from './contexts/ToastContext';
import './TakeAttendancePage.css';

interface Student {
  id: string;
  name: string;
  rollNumber: string;
  faceEmbedding?: number[];
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
  timeSlot: number; // in minutes
  maxStudents: number;
  detectedStudents: AttendanceRecord[];
  isActive: boolean;
  startTime: Date;
}

const TakeAttendancePage: React.FC = () => {
  const { code } = useParams<{ code: string }>();
  const navigate = useNavigate();
  const { addToast } = useToast();
  
  // State management
  const [isInitialized, setIsInitialized] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [timeSlot, setTimeSlot] = useState(5); // Default 5 minutes
  const [maxStudents] = useState(6); // Fixed to 6 as per requirement
  const [currentSession, setCurrentSession] = useState<AttendanceSession | null>(null);
  const [registeredStudents, setRegisteredStudents] = useState<Student[]>([]);
  const [detectedFaces, setDetectedFaces] = useState<AttendanceRecord[]>([]);
  const [timeRemaining, setTimeRemaining] = useState(0);
  const [isProcessing, setIsProcessing] = useState(false);
  
  // Refs
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  
  // Initialize camera and face detection
  const initializeCamera = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 1280 },
          height: { ideal: 720 },
          facingMode: 'user'
        },
        audio: false
      });
      
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        streamRef.current = stream;
        setIsInitialized(true);
        addToast({ message: 'Camera initialized successfully', type: 'success' });
      }
    } catch (error) {
      console.error('Error accessing camera:', error);
      addToast({ message: 'Failed to access camera. Please check permissions.', type: 'error' });
    }
  }, [addToast]);

  // Load registered students from backend
  const loadRegisteredStudents = useCallback(async () => {
    try {
      // Mock data - replace with actual API call
      const mockStudents: Student[] = [
        {
          id: '1',
          name: 'John Doe',
          rollNumber: 'CS001',
          profileImage: '/api/placeholder/150/150'
        },
        {
          id: '2',
          name: 'Jane Smith',
          rollNumber: 'CS002',
          profileImage: '/api/placeholder/150/150'
        },
        {
          id: '3',
          name: 'Mike Johnson',
          rollNumber: 'CS003',
          profileImage: '/api/placeholder/150/150'
        },
        {
          id: '4',
          name: 'Sarah Wilson',
          rollNumber: 'CS004',
          profileImage: '/api/placeholder/150/150'
        },
        {
          id: '5',
          name: 'David Brown',
          rollNumber: 'CS005',
          profileImage: '/api/placeholder/150/150'
        },
        {
          id: '6',
          name: 'Lisa Davis',
          rollNumber: 'CS006',
          profileImage: '/api/placeholder/150/150'
        }
      ];
      
      setRegisteredStudents(mockStudents);
      addToast({ message: `Loaded ${mockStudents.length} registered students`, type: 'success' });
    } catch (error) {
      console.error('Error loading students:', error);
      addToast({ message: 'Failed to load registered students', type: 'error' });
    }
  }, [addToast]);

  // Process frame for face recognition (API call to backend)
  const processFrameForFaceRecognition = useCallback(async (imageBlob: Blob) => {
    try {
      const formData = new FormData();
      formData.append('image', imageBlob);
      formData.append('classroomCode', code || '');
      formData.append('sessionId', currentSession?.sessionId || '');
      
      // Mock response - replace with actual API call
      const mockDetection = Math.random() > 0.7; // 30% chance of detection
      
      if (mockDetection && detectedFaces.length < maxStudents) {
        const availableStudents = registeredStudents.filter(
          student => !detectedFaces.some(detected => detected.studentId === student.id)
        );
        
        if (availableStudents.length > 0) {
          const randomStudent = availableStudents[Math.floor(Math.random() * availableStudents.length)];
          const newDetection: AttendanceRecord = {
            studentId: randomStudent.id,
            name: randomStudent.name,
            rollNumber: randomStudent.rollNumber,
            timestamp: new Date(),
            confidence: 0.85 + Math.random() * 0.1 // 85-95% confidence
          };
          
          setDetectedFaces(prev => [...prev, newDetection]);
          addToast({ message: `Detected: ${newDetection.name} (${(newDetection.confidence * 100).toFixed(1)}%)`, type: 'success' });
        }
      }
      
    } catch (error) {
      console.error('Error processing frame:', error);
    }
  }, [code, currentSession?.sessionId, detectedFaces, maxStudents, registeredStudents, addToast]);

  // Face detection and recognition function
  const detectAndRecognizeFaces = useCallback(async () => {
    if (!videoRef.current || !canvasRef.current || !isRecording) return;
    
    setIsProcessing(true);
    
    try {
      const video = videoRef.current;
      const canvas = canvasRef.current;
      const ctx = canvas.getContext('2d');
      
      if (!ctx) return;
      
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      ctx.drawImage(video, 0, 0);
      
      // Convert canvas to blob for API call
      canvas.toBlob(async (blob) => {
        if (blob) {
          await processFrameForFaceRecognition(blob);
        }
      }, 'image/jpeg', 0.8);
      
    } catch (error) {
      console.error('Error in face detection:', error);
    } finally {
      setIsProcessing(false);
    }
  }, [isRecording, processFrameForFaceRecognition]);

  // Start attendance session
  const startAttendanceSession = async () => {
    if (!code) return;
    
    const session: AttendanceSession = {
      sessionId: `session_${Date.now()}`,
      classroomCode: code,
      timeSlot,
      maxStudents,
      detectedStudents: [],
      isActive: true,
      startTime: new Date()
    };
    
    setCurrentSession(session);
    setIsRecording(true);
    setTimeRemaining(timeSlot * 60); // Convert minutes to seconds
    setDetectedFaces([]);
    
    addToast({ message: `Attendance session started for ${timeSlot} minutes`, type: 'success' });
    
    // Start timer
    intervalRef.current = setInterval(() => {
      setTimeRemaining(prev => {
        if (prev <= 1) {
          endAttendanceSession();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
  };

  // End attendance session
  const endAttendanceSession = async () => {
    setIsRecording(false);
    
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
    
    if (currentSession) {
      const updatedSession = {
        ...currentSession,
        detectedStudents: detectedFaces,
        isActive: false
      };
      
      // Save session to backend
      try {
        // Mock API call - replace with actual implementation
        console.log('Saving attendance session:', updatedSession);
        addToast({ message: 'Attendance session completed successfully', type: 'success' });
        
        // Navigate to results page
        navigate(`/classroom/${code}/attendance/results`, {
          state: {
            session: updatedSession,
            presentStudents: detectedFaces,
            absentStudents: registeredStudents.filter(
              student => !detectedFaces.some(detected => detected.studentId === student.id)
            )
          }
        });
        
      } catch (error) {
        console.error('Error saving attendance:', error);
        addToast({ message: 'Failed to save attendance data', type: 'error' });
      }
    }
  };

  // Format time display
  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  // Initialize component
  useEffect(() => {
    loadRegisteredStudents();
    initializeCamera();
    
    return () => {
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [loadRegisteredStudents, initializeCamera]);

  // Face detection loop
  useEffect(() => {
    if (isRecording) {
      const detectionInterval = setInterval(detectAndRecognizeFaces, 2000); // Check every 2 seconds
      return () => clearInterval(detectionInterval);
    }
  }, [isRecording, detectAndRecognizeFaces]);

  return (
    <div className="attendance-page">
      <div className="attendance-header">
        <button 
          className="back-button"
          onClick={() => navigate(`/classroom/${code}`)}
        >
          ← Back to Classroom
        </button>
        <h1>Facial Recognition Attendance</h1>
        <div className="header-info">
          <span>Classroom: {code}</span>
          <span>Max Students: {maxStudents}</span>
        </div>
      </div>

      <div className="attendance-content">
        {/* Camera Section */}
        <div className="camera-section">
          <div className="camera-container">
            <video
              ref={videoRef}
              autoPlay
              playsInline
              muted
              className="camera-feed"
            />
            <canvas
              ref={canvasRef}
              className="detection-canvas hidden"
            />
            
            {isRecording && (
              <div className="recording-overlay">
                <div className="recording-indicator">
                  <div className="recording-dot"></div>
                  <span>RECORDING</span>
                </div>
                <div className="time-remaining">
                  {formatTime(timeRemaining)}
                </div>
                <div className="detection-count">
                  {detectedFaces.length}/{maxStudents} detected
                </div>
              </div>
            )}
            
            {isProcessing && (
              <div className="processing-indicator">
                <div className="spinner"></div>
                <span>Processing...</span>
              </div>
            )}
          </div>

          <div className="camera-controls">
            {!isRecording ? (
              <>
                <div className="time-slot-selector">
                  <label htmlFor="timeSlot">Session Duration (minutes):</label>
                  <select
                    id="timeSlot"
                    value={timeSlot}
                    onChange={(e) => setTimeSlot(Number(e.target.value))}
                    className="time-select"
                  >
                    <option value={3}>3 minutes</option>
                    <option value={5}>5 minutes</option>
                    <option value={10}>10 minutes</option>
                    <option value={15}>15 minutes</option>
                  </select>
                </div>
                
                <button
                  className="start-session-btn"
                  onClick={startAttendanceSession}
                  disabled={!isInitialized || registeredStudents.length === 0}
                >
                  Start Attendance Session
                </button>
              </>
            ) : (
              <button
                className="end-session-btn"
                onClick={endAttendanceSession}
              >
                End Session Early
              </button>
            )}
          </div>
        </div>

        {/* Students Section */}
        <div className="students-section">
          <div className="detected-students">
            <h3>Detected Students ({detectedFaces.length}/{maxStudents})</h3>
            <div className="students-grid">
              {detectedFaces.map((record) => (
                <div key={record.studentId} className="student-card detected">
                  <div className="student-avatar">
                    <img 
                      src={`/api/placeholder/80/80`} 
                      alt={record.name}
                      onError={(e) => {
                        (e.target as HTMLImageElement).src = '/api/placeholder/80/80';
                      }}
                    />
                    <div className="detection-badge">✓</div>
                  </div>
                  <div className="student-info">
                    <div className="student-name">{record.name}</div>
                    <div className="student-roll">{record.rollNumber}</div>
                    <div className="detection-time">
                      {record.timestamp.toLocaleTimeString()}
                    </div>
                    <div className="confidence-score">
                      {(record.confidence * 100).toFixed(1)}% confidence
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="registered-students">
            <h3>Registered Students ({registeredStudents.length})</h3>
            <div className="students-list">
              {registeredStudents.map((student) => {
                const isDetected = detectedFaces.some(d => d.studentId === student.id);
                return (
                  <div 
                    key={student.id} 
                    className={`student-item ${isDetected ? 'present' : 'pending'}`}
                  >
                    <img 
                      src={student.profileImage || '/api/placeholder/40/40'} 
                      alt={student.name}
                      className="student-avatar-small"
                    />
                    <div className="student-details">
                      <span className="name">{student.name}</span>
                      <span className="roll">{student.rollNumber}</span>
                    </div>
                    <div className={`status-indicator ${isDetected ? 'present' : 'pending'}`}>
                      {isDetected ? '✓' : '⏳'}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TakeAttendancePage;
