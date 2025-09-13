import React, { useState, useRef, useCallback, useEffect } from 'react';
import jsPDF from 'jspdf';
import { useToast } from '../contexts/ToastContext';
import '../types/speechRecognition.d.ts';
import './LectureRecorder.css';

interface LectureRecorderProps {
  subject: string;
  topic: string;
  date: string;
  teacherName: string;
  onRecordingComplete: (pdfUrl: string) => void;
}

interface TranscriptSegment {
  text: string;
  timestamp: Date;
  confidence: number;
}

const LectureRecorder: React.FC<LectureRecorderProps> = ({
  subject,
  topic,
  date,
  teacherName,
  onRecordingComplete
}) => {
  const [isRecording, setIsRecording] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [transcript, setTranscript] = useState<TranscriptSegment[]>([]);
  const [currentText, setCurrentText] = useState('');
  const [recordingDuration, setRecordingDuration] = useState(0);
  const [isProcessing, setIsProcessing] = useState(false);
  const [correctedText, setCorrectedText] = useState('');
  const [hasPermission, setHasPermission] = useState<boolean | null>(null);

  const recognitionRef = useRef<any | null>(null);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const startTimeRef = useRef<Date | null>(null);
  const { addToast } = useToast();

  // Request microphone permission
  const requestMicrophonePermission = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      stream.getTracks().forEach(track => track.stop());
      setHasPermission(true);
      addToast({
        message: 'Microphone access granted!',
        type: 'success',
        duration: 3000
      });
    } catch (error) {
      console.error('Error requesting microphone permission:', error);
      setHasPermission(false);
      addToast({
        message: 'Microphone access denied. Please enable microphone permissions.',
        type: 'error',
        duration: 5000
      });
    }
  }, [addToast]);

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
          addToast({
            message: `Recording error: ${event.error}`,
            type: 'error',
            duration: 5000
          });
        };

        recognitionRef.current.onend = () => {
          if (isRecording && !isPaused) {
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
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [isRecording, isPaused, addToast]);

  // Check microphone permission
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

  useEffect(() => {
    checkMicrophonePermission();
  }, []);

  // Request microphone permission (duplicate removed)

  // Start recording
  const startRecording = useCallback(async () => {
    if (!hasPermission) {
      await requestMicrophonePermission();
      return;
    }

    if (!recognitionRef.current) {
      addToast({
        message: 'Speech recognition not supported in this browser',
        type: 'error',
        duration: 5000
      });
      return;
    }

    try {
      setIsRecording(true);
      setIsPaused(false);
      setTranscript([]);
      setCurrentText('');
      setRecordingDuration(0);
      startTimeRef.current = new Date();

      recognitionRef.current.start();

      // Start duration timer
      intervalRef.current = setInterval(() => {
        if (startTimeRef.current) {
          const elapsed = Math.floor((Date.now() - startTimeRef.current.getTime()) / 1000);
          setRecordingDuration(elapsed);
        }
      }, 1000);

      addToast({
        message: 'Recording started! Speak clearly into your microphone.',
        type: 'success',
        duration: 3000
      });
    } catch (error) {
      console.error('Error starting recording:', error);
      addToast({
        message: 'Failed to start recording. Please try again.',
        type: 'error',
        duration: 5000
      });
    }
  }, [hasPermission, addToast, requestMicrophonePermission]);

  // Pause/Resume recording
  const togglePause = useCallback(() => {
    if (!recognitionRef.current) return;

    if (isPaused) {
      // Resume
      setIsPaused(false);
      recognitionRef.current.start();
      addToast({
        message: 'Recording resumed',
        type: 'info',
        duration: 2000
      });
    } else {
      // Pause
      setIsPaused(true);
      recognitionRef.current.stop();
      addToast({
        message: 'Recording paused',
        type: 'warning',
        duration: 2000
      });
    }
  }, [isPaused, addToast]);

  // Simple grammar correction (mock implementation)
  const correctGrammar = (text: string): string => {
    // Basic grammar corrections
    let corrected = text
      // Capitalize first letter
      .replace(/^[a-z]/, (match) => match.toUpperCase())
      // Add periods after sentences
      .replace(/([a-z])\s+([A-Z])/g, '$1. $2')
      // Fix common contractions
      .replace(/\bi am\b/gi, 'I am')
      .replace(/\bi'll\b/gi, 'I\'ll')
      .replace(/\bi've\b/gi, 'I\'ve')
      .replace(/\bwont\b/gi, 'won\'t')
      .replace(/\bcant\b/gi, 'can\'t')
      .replace(/\bdont\b/gi, 'don\'t')
      // Fix spacing around punctuation
      .replace(/\s+([,.!?])/g, '$1')
      .replace(/([,.!?])([a-zA-Z])/g, '$1 $2')
      // Remove extra spaces
      .replace(/\s+/g, ' ')
      .trim();

    // Ensure it ends with proper punctuation
    if (corrected && !corrected.match(/[.!?]$/)) {
      corrected += '.';
    }

    return corrected;
  };

  // Stop recording and generate PDF
  const stopRecording = useCallback(async () => {
    if (!recognitionRef.current) return;

    setIsRecording(false);
    setIsPaused(false);
    recognitionRef.current.stop();

    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }

    setIsProcessing(true);

    try {
      // Combine all transcript segments
      const fullTranscript = transcript
        .map(segment => segment.text)
        .join(' ')
        .trim();

      if (!fullTranscript) {
        addToast({
          message: 'No speech detected during recording',
          type: 'warning',
          duration: 4000
        });
        setIsProcessing(false);
        return;
      }

      // Apply grammar correction
      const corrected = correctGrammar(fullTranscript);
      setCorrectedText(corrected);

      // Generate PDF
      const pdf = new jsPDF();
      const pageWidth = pdf.internal.pageSize.getWidth();
      const margin = 20;
      const maxWidth = pageWidth - 2 * margin;

      // Header
      pdf.setFontSize(20);
      pdf.setFont('helvetica', 'bold');
      pdf.text('Class Lecture Recording', margin, 30);

      // Lecture details
      pdf.setFontSize(12);
      pdf.setFont('helvetica', 'normal');
      let yPosition = 50;

      const details = [
        `Subject: ${subject}`,
        `Topic: ${topic}`,
        `Date: ${new Date(date).toLocaleDateString()}`,
        `Teacher: ${teacherName}`,
        `Duration: ${Math.floor(recordingDuration / 60)}:${(recordingDuration % 60).toString().padStart(2, '0')}`,
        `Recorded on: ${new Date().toLocaleString()}`
      ];

      details.forEach(detail => {
        pdf.text(detail, margin, yPosition);
        yPosition += 8;
      });

      // Separator line
      yPosition += 10;
      pdf.line(margin, yPosition, pageWidth - margin, yPosition);
      yPosition += 15;

      // Transcript heading
      pdf.setFontSize(14);
      pdf.setFont('helvetica', 'bold');
      pdf.text('Lecture Transcript', margin, yPosition);
      yPosition += 15;

      // Transcript content
      pdf.setFontSize(11);
      pdf.setFont('helvetica', 'normal');
      
      const lines = pdf.splitTextToSize(corrected, maxWidth);
      lines.forEach((line: string) => {
        if (yPosition > pdf.internal.pageSize.getHeight() - margin) {
          pdf.addPage();
          yPosition = margin;
        }
        pdf.text(line, margin, yPosition);
        yPosition += 6;
      });

      // Footer
      const pageCount = pdf.getNumberOfPages();
      for (let i = 1; i <= pageCount; i++) {
        pdf.setPage(i);
        pdf.setFontSize(8);
        pdf.setFont('helvetica', 'normal');
        pdf.text(
          `Generated by ClassroomAI - Page ${i} of ${pageCount}`,
          margin,
          pdf.internal.pageSize.getHeight() - 10
        );
      }

      // Generate filename
      const filename = `lecture-${subject.toLowerCase().replace(/\s+/g, '-')}-${topic.toLowerCase().replace(/\s+/g, '-')}-${new Date(date).toISOString().split('T')[0]}.pdf`;
      
      // Save PDF
      pdf.save(filename);

      // Create blob URL for display
      const pdfBlob = pdf.output('blob');
      const pdfUrl = URL.createObjectURL(pdfBlob);

      onRecordingComplete(pdfUrl);

      addToast({
        message: `Lecture recording saved as ${filename}`,
        type: 'success',
        duration: 5000
      });

    } catch (error) {
      console.error('Error generating PDF:', error);
      addToast({
        message: 'Failed to generate PDF. Please try again.',
        type: 'error',
        duration: 5000
      });
    } finally {
      setIsProcessing(false);
    }
  }, [transcript, recordingDuration, subject, topic, date, teacherName, onRecordingComplete, addToast]);

  // Format duration
  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  // Get current transcript text
  const getCurrentTranscript = () => {
    const fullTranscript = transcript.map(segment => segment.text).join(' ');
    return fullTranscript + (currentText ? ` ${currentText}` : '');
  };

  if (hasPermission === null) {
    return (
      <div className="lecture-recorder loading">
        <div className="loading-spinner"></div>
        <p>Checking microphone permissions...</p>
      </div>
    );
  }

  if (hasPermission === false) {
    return (
      <div className="lecture-recorder permission-required">
        <div className="permission-content">
          <div className="mic-icon">🎤</div>
          <h3>Microphone Access Required</h3>
          <p>To record lectures, please allow microphone access in your browser.</p>
          <button className="permission-btn" onClick={requestMicrophonePermission}>
            Grant Microphone Access
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="lecture-recorder">
      <div className="recorder-header">
        <div className="recording-info">
          <h3>🎓 Lecture Recording</h3>
          <div className="lecture-details">
            <span>{subject} - {topic}</span>
            <span>{teacherName}</span>
          </div>
        </div>
        
        <div className="recording-status">
          {isRecording && (
            <>
              <div className={`recording-indicator ${isPaused ? 'paused' : 'active'}`}>
                <div className="pulse-dot"></div>
                {isPaused ? 'PAUSED' : 'RECORDING'}
              </div>
              <div className="duration">{formatDuration(recordingDuration)}</div>
            </>
          )}
        </div>
      </div>

      <div className="recorder-controls">
        {!isRecording ? (
          <button className="start-btn" onClick={startRecording} disabled={isProcessing}>
            {isProcessing ? '⏳ Processing...' : '🎙️ Start Recording'}
          </button>
        ) : (
          <div className="recording-controls">
            <button className="pause-btn" onClick={togglePause}>
              {isPaused ? '▶️ Resume' : '⏸️ Pause'}
            </button>
            <button className="stop-btn" onClick={stopRecording}>
              ⏹️ Stop & Generate PDF
            </button>
          </div>
        )}
      </div>

      {(isRecording || transcript.length > 0) && (
        <div className="transcript-container">
          <div className="transcript-header">
            <h4>📝 Live Transcript</h4>
            <div className="transcript-stats">
              {transcript.length} segments • {getCurrentTranscript().split(' ').length} words
            </div>
          </div>
          
          <div className="transcript-content">
            {transcript.map((segment, index) => (
              <div key={index} className="transcript-segment">
                <span className="timestamp">
                  {segment.timestamp.toLocaleTimeString()}
                </span>
                <span className="text">{segment.text}</span>
                <span className="confidence">
                  {Math.round(segment.confidence * 100)}%
                </span>
              </div>
            ))}
            
            {currentText && (
              <div className="transcript-segment interim">
                <span className="timestamp">
                  {new Date().toLocaleTimeString()}
                </span>
                <span className="text">{currentText}</span>
                <span className="confidence">...</span>
              </div>
            )}
          </div>
          
          {!isRecording && correctedText && (
            <div className="corrected-text">
              <h4>✨ Grammar-Corrected Text</h4>
              <div className="corrected-content">
                {correctedText}
              </div>
            </div>
          )}
        </div>
      )}

      {isProcessing && (
        <div className="processing-overlay">
          <div className="processing-content">
            <div className="loading-spinner"></div>
            <h3>Processing Lecture Recording...</h3>
            <p>Applying grammar corrections and generating PDF...</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default LectureRecorder;