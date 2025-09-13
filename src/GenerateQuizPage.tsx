import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useToast } from './contexts/ToastContext';
import ThemeToggle from './components/ThemeToggle';
import LoadingSpinner from './components/LoadingSpinner';
import './components/QuizPage.css';

interface Question {
  id: string;
  question: string;
  options: string[];
  correct: number;
  explanation?: string;
  difficulty: 'easy' | 'medium' | 'hard';
  topic: string;
}

interface QuizConfig {
  subject: string;
  topic: string;
  difficulty: 'easy' | 'medium' | 'hard' | 'mixed';
  questionCount: number;
  timeLimit: number; // in minutes
  questionTypes: string[];
}

const GenerateQuizPage: React.FC = () => {
  const navigate = useNavigate();
  const { addToast } = useToast();
  
  const [quizConfig, setQuizConfig] = useState<QuizConfig>({
    subject: '',
    topic: '',
    difficulty: 'medium',
    questionCount: 10,
    timeLimit: 15,
    questionTypes: ['multiple-choice']
  });
  
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedQuiz, setGeneratedQuiz] = useState<Question[]>([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [selectedAnswers, setSelectedAnswers] = useState<{[key: string]: number}>({});
  const [isQuizStarted, setIsQuizStarted] = useState(false);
  const [isQuizCompleted, setIsQuizCompleted] = useState(false);
  const [timeRemaining, setTimeRemaining] = useState(0);
  const [quizResults, setQuizResults] = useState<any>(null);

  // Sample question bank - In real app, this would come from API
  const questionBank: Question[] = [
    // Math Questions
    {
      id: '1',
      question: 'What is the derivative of x²?',
      options: ['2x', 'x', '2', 'x²'],
      correct: 0,
      explanation: 'The derivative of x² is 2x using the power rule.',
      difficulty: 'easy',
      topic: 'calculus'
    },
    {
      id: '2',
      question: 'What is the integral of 2x?',
      options: ['x²', 'x² + C', '2', '2x + C'],
      correct: 1,
      explanation: 'The integral of 2x is x² + C, where C is the constant of integration.',
      difficulty: 'medium',
      topic: 'calculus'
    },
    {
      id: '3',
      question: 'What is the value of sin(π/2)?',
      options: ['0', '1', '-1', 'π/2'],
      correct: 1,
      explanation: 'sin(π/2) = 1, as π/2 radians equals 90 degrees.',
      difficulty: 'easy',
      topic: 'trigonometry'
    },
    // Physics Questions
    {
      id: '4',
      question: 'What is Newton\'s second law of motion?',
      options: ['F = ma', 'E = mc²', 'v = u + at', 'P = mv'],
      correct: 0,
      explanation: 'Newton\'s second law states that Force equals mass times acceleration (F = ma).',
      difficulty: 'easy',
      topic: 'mechanics'
    },
    {
      id: '5',
      question: 'What is the speed of light in vacuum?',
      options: ['3 × 10⁸ m/s', '3 × 10⁶ m/s', '9 × 10⁸ m/s', '1 × 10⁸ m/s'],
      correct: 0,
      explanation: 'The speed of light in vacuum is approximately 3 × 10⁸ m/s.',
      difficulty: 'medium',
      topic: 'optics'
    },
    // Chemistry Questions
    {
      id: '6',
      question: 'What is the chemical symbol for Gold?',
      options: ['Go', 'Gd', 'Au', 'Ag'],
      correct: 2,
      explanation: 'Au comes from the Latin word "aurum" meaning gold.',
      difficulty: 'easy',
      topic: 'periodic-table'
    },
    {
      id: '7',
      question: 'What is Avogadro\'s number?',
      options: ['6.022 × 10²³', '6.022 × 10²²', '3.14 × 10²³', '1.602 × 10⁻¹⁹'],
      correct: 0,
      explanation: 'Avogadro\'s number is 6.022 × 10²³ particles per mole.',
      difficulty: 'medium',
      topic: 'molecular-theory'
    }
  ];

  const subjects = ['Mathematics', 'Physics', 'Chemistry', 'Biology'];
  const topics = {
    'Mathematics': ['Algebra', 'Calculus', 'Trigonometry', 'Geometry', 'Statistics'],
    'Physics': ['Mechanics', 'Thermodynamics', 'Optics', 'Electromagnetism', 'Quantum Physics'],
    'Chemistry': ['Periodic Table', 'Organic Chemistry', 'Inorganic Chemistry', 'Physical Chemistry', 'Molecular Theory'],
    'Biology': ['Cell Biology', 'Genetics', 'Evolution', 'Ecology', 'Human Anatomy']
  };

  const generateQuiz = () => {
    setIsGenerating(true);
    
    // Filter questions based on config
    let filteredQuestions = questionBank.filter(q => {
      const subjectMatch = q.topic.toLowerCase().includes(quizConfig.topic.toLowerCase().replace(' ', '-')) ||
                          quizConfig.topic === '';
      const difficultyMatch = quizConfig.difficulty === 'mixed' || q.difficulty === quizConfig.difficulty;
      return subjectMatch && difficultyMatch;
    });

    // If no specific questions found, use all questions
    if (filteredQuestions.length === 0) {
      filteredQuestions = questionBank;
    }

    // Shuffle and select questions
    const shuffled = filteredQuestions.sort(() => Math.random() - 0.5);
    const selected = shuffled.slice(0, Math.min(quizConfig.questionCount, shuffled.length));

    setTimeout(() => {
      setGeneratedQuiz(selected);
      setIsGenerating(false);
      addToast({
        message: `Quiz generated with ${selected.length} questions!`,
        type: 'success',
        duration: 3000
      });
    }, 1500);
  };

  const startQuiz = () => {
    if (generatedQuiz.length === 0) {
      addToast({
        message: 'Please generate a quiz first!',
        type: 'warning',
        duration: 3000
      });
      return;
    }
    
    setIsQuizStarted(true);
    setCurrentQuestionIndex(0);
    setSelectedAnswers({});
    setTimeRemaining(quizConfig.timeLimit * 60); // Convert to seconds
    
    // Start timer
    const timer = setInterval(() => {
      setTimeRemaining(prev => {
        if (prev <= 1) {
          clearInterval(timer);
          completeQuiz();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
  };

  const selectAnswer = (questionId: string, answerIndex: number) => {
    setSelectedAnswers(prev => ({
      ...prev,
      [questionId]: answerIndex
    }));
  };

  const nextQuestion = () => {
    if (currentQuestionIndex < generatedQuiz.length - 1) {
      setCurrentQuestionIndex(prev => prev + 1);
    } else {
      completeQuiz();
    }
  };

  const completeQuiz = () => {
    const results = calculateResults();
    setQuizResults(results);
    setIsQuizCompleted(true);
    setIsQuizStarted(false);
    
    addToast({
      message: `Quiz completed! Score: ${results.percentage}%`,
      type: 'success',
      duration: 5000
    });
  };

  const calculateResults = () => {
    let correct = 0;
    let total = generatedQuiz.length;
    
    generatedQuiz.forEach(question => {
      if (selectedAnswers[question.id] === question.correct) {
        correct++;
      }
    });
    
    const percentage = Math.round((correct / total) * 100);
    
    return {
      correct,
      total,
      percentage,
      grade: percentage >= 90 ? 'A' : percentage >= 80 ? 'B' : percentage >= 70 ? 'C' : percentage >= 60 ? 'D' : 'F',
      timeTaken: quizConfig.timeLimit - Math.floor(timeRemaining / 60)
    };
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const resetQuiz = () => {
    setIsQuizStarted(false);
    setIsQuizCompleted(false);
    setCurrentQuestionIndex(0);
    setSelectedAnswers({});
    setQuizResults(null);
    setGeneratedQuiz([]);
  };

  if (isQuizCompleted && quizResults) {
    return (
      <div className="quiz-container">
        <div className="quiz-header">
          <h1>Quiz Results</h1>
          <ThemeToggle />
        </div>
        
        <div className="quiz-results">
          <div className="results-card">
            <div className="score-display">
              <div className="score-circle">
                <span className="score-number">{quizResults.percentage}%</span>
                <span className="score-grade">Grade: {quizResults.grade}</span>
              </div>
            </div>
            
            <div className="results-details">
              <div className="result-item">
                <span className="label">Correct Answers:</span>
                <span className="value">{quizResults.correct} / {quizResults.total}</span>
              </div>
              <div className="result-item">
                <span className="label">Time Taken:</span>
                <span className="value">{quizResults.timeTaken} minutes</span>
              </div>
              <div className="result-item">
                <span className="label">Subject:</span>
                <span className="value">{quizConfig.subject}</span>
              </div>
              <div className="result-item">
                <span className="label">Difficulty:</span>
                <span className="value">{quizConfig.difficulty}</span>
              </div>
            </div>
            
            <div className="results-actions">
              <button className="quiz-btn primary" onClick={resetQuiz}>
                Take Another Quiz
              </button>
              <button className="quiz-btn secondary" onClick={() => navigate(-1)}>
                Back to Classroom
              </button>
            </div>
          </div>
          
          <div className="question-review">
            <h3>Question Review</h3>
            {generatedQuiz.map((question, index) => (
              <div key={question.id} className="review-item">
                <div className="question-header">
                  <span className="question-number">Q{index + 1}</span>
                  <span className={`result-indicator ${selectedAnswers[question.id] === question.correct ? 'correct' : 'incorrect'}`}>
                    {selectedAnswers[question.id] === question.correct ? '✓' : '✗'}
                  </span>
                </div>
                <p className="question-text">{question.question}</p>
                <div className="answer-review">
                  <p><strong>Your Answer:</strong> {question.options[selectedAnswers[question.id]] || 'Not answered'}</p>
                  <p><strong>Correct Answer:</strong> {question.options[question.correct]}</p>
                  {question.explanation && (
                    <p className="explanation"><strong>Explanation:</strong> {question.explanation}</p>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (isQuizStarted && generatedQuiz.length > 0) {
    const currentQuestion = generatedQuiz[currentQuestionIndex];
    
    return (
      <div className="quiz-container">
        <div className="quiz-header">
          <div className="quiz-progress">
            <span>Question {currentQuestionIndex + 1} of {generatedQuiz.length}</span>
            <div className="progress-bar">
              <div 
                className={`progress-fill progress-${Math.round(((currentQuestionIndex + 1) / generatedQuiz.length) * 100)}`}
              ></div>
            </div>
          </div>
          <div className="quiz-timer">
            <span className={timeRemaining < 60 ? 'timer-warning' : ''}>
              ⏱️ {formatTime(timeRemaining)}
            </span>
          </div>
        </div>
        
        <div className="question-card">
          <div className="question-header">
            <span className="question-difficulty">{currentQuestion.difficulty}</span>
            <span className="question-topic">{currentQuestion.topic}</span>
          </div>
          
          <h2 className="question-text">{currentQuestion.question}</h2>
          
          <div className="options-container">
            {currentQuestion.options.map((option, index) => (
              <button
                key={index}
                className={`option-btn ${selectedAnswers[currentQuestion.id] === index ? 'selected' : ''}`}
                onClick={() => selectAnswer(currentQuestion.id, index)}
              >
                <span className="option-letter">{String.fromCharCode(65 + index)}</span>
                <span className="option-text">{option}</span>
              </button>
            ))}
          </div>
          
          <div className="question-actions">
            <button 
              className="quiz-btn secondary" 
              onClick={() => setCurrentQuestionIndex(Math.max(0, currentQuestionIndex - 1))}
              disabled={currentQuestionIndex === 0}
            >
              Previous
            </button>
            <button 
              className="quiz-btn primary" 
              onClick={nextQuestion}
              disabled={selectedAnswers[currentQuestion.id] === undefined}
            >
              {currentQuestionIndex === generatedQuiz.length - 1 ? 'Finish Quiz' : 'Next Question'}
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="quiz-container">
      <div className="quiz-header">
        <h1>Generate Quiz</h1>
        <ThemeToggle />
      </div>
      
      <div className="quiz-generator">
        <div className="config-section">
          <h2>Quiz Configuration</h2>
          
          <div className="config-grid">
            <div className="config-item">
              <label>Subject</label>
              <select 
                value={quizConfig.subject} 
                onChange={(e) => setQuizConfig(prev => ({ ...prev, subject: e.target.value, topic: '' }))}
                aria-label="Select subject for quiz"
              >
                <option value="">Select Subject</option>
                {subjects.map(subject => (
                  <option key={subject} value={subject}>{subject}</option>
                ))}
              </select>
            </div>
            
            <div className="config-item">
              <label>Topic</label>
              <select 
                value={quizConfig.topic} 
                onChange={(e) => setQuizConfig(prev => ({ ...prev, topic: e.target.value }))}
                disabled={!quizConfig.subject}
                aria-label="Select topic for quiz"
              >
                <option value="">Select Topic</option>
                {quizConfig.subject && topics[quizConfig.subject as keyof typeof topics]?.map(topic => (
                  <option key={topic} value={topic}>{topic}</option>
                ))}
              </select>
            </div>
            
            <div className="config-item">
              <label>Difficulty</label>
              <select 
                value={quizConfig.difficulty} 
                onChange={(e) => setQuizConfig(prev => ({ ...prev, difficulty: e.target.value as any }))}
                aria-label="Select difficulty level"
              >
                <option value="easy">Easy</option>
                <option value="medium">Medium</option>
                <option value="hard">Hard</option>
                <option value="mixed">Mixed</option>
              </select>
            </div>
            
            <div className="config-item">
              <label>Number of Questions</label>
              <select 
                value={quizConfig.questionCount} 
                onChange={(e) => setQuizConfig(prev => ({ ...prev, questionCount: parseInt(e.target.value) }))}
                aria-label="Select number of questions"
              >
                <option value={5}>5 Questions</option>
                <option value={10}>10 Questions</option>
                <option value={15}>15 Questions</option>
                <option value={20}>20 Questions</option>
              </select>
            </div>
            
            <div className="config-item">
              <label>Time Limit (minutes)</label>
              <select 
                value={quizConfig.timeLimit} 
                onChange={(e) => setQuizConfig(prev => ({ ...prev, timeLimit: parseInt(e.target.value) }))}
                aria-label="Select time limit in minutes"
              >
                <option value={5}>5 Minutes</option>
                <option value={10}>10 Minutes</option>
                <option value={15}>15 Minutes</option>
                <option value={30}>30 Minutes</option>
                <option value={60}>60 Minutes</option>
              </select>
            </div>
          </div>
          
          <div className="generator-actions">
            <button 
              className="quiz-btn primary large" 
              onClick={generateQuiz}
              disabled={isGenerating || !quizConfig.subject}
            >
              {isGenerating ? (
                <>
                  <LoadingSpinner size="small" color="white" />
                  Generating Quiz...
                </>
              ) : (
                '🎯 Generate Quiz'
              )}
            </button>
          </div>
        </div>
        
        {generatedQuiz.length > 0 && (
          <div className="quiz-preview">
            <h3>Quiz Preview</h3>
            <div className="preview-stats">
              <div className="stat-item">
                <span className="stat-label">Questions:</span>
                <span className="stat-value">{generatedQuiz.length}</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Time Limit:</span>
                <span className="stat-value">{quizConfig.timeLimit} min</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Difficulty:</span>
                <span className="stat-value">{quizConfig.difficulty}</span>
              </div>
            </div>
            
            <div className="preview-questions">
              {generatedQuiz.slice(0, 3).map((question, index) => (
                <div key={question.id} className="preview-question">
                  <span className="preview-number">Q{index + 1}</span>
                  <span className="preview-text">{question.question}</span>
                  <span className="preview-difficulty">{question.difficulty}</span>
                </div>
              ))}
              {generatedQuiz.length > 3 && (
                <div className="preview-more">
                  ... and {generatedQuiz.length - 3} more questions
                </div>
              )}
            </div>
            
            <button 
              className="quiz-btn success large" 
              onClick={startQuiz}
            >
              🚀 Start Quiz
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default GenerateQuizPage;
