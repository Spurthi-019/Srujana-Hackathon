import { UserButton } from '@clerk/clerk-react';
import React, { useEffect, useState } from 'react';
import ThemeToggle from './components/ThemeToggle';
import './Leaderboard.css';

// Mock data for 40 students with their quiz scores
const generateMockStudents = () => {
  const names = [
    'Alice Johnson', 'Bob Smith', 'Charlie Brown', 'Diana Prince', 'Edward Norton',
    'Fiona Green', 'George Wilson', 'Hannah Lee', 'Ian Parker', 'Julia Roberts',
    'Kevin Hart', 'Laura Davis', 'Michael Scott', 'Nina Williams', 'Oscar Wilde',
    'Paula Abdul', 'Quincy Jones', 'Rachel Green', 'Samuel Jackson', 'Tina Turner',
    'Uma Thurman', 'Victor Hugo', 'Wendy Williams', 'Xavier Woods', 'Yasmin Ali',
    'Zachary Taylor', 'Amy Adams', 'Brian Cox', 'Catherine Zeta', 'Daniel Craig',
    'Emma Stone', 'Frank Miller', 'Grace Kelly', 'Henry Ford', 'Ivy League',
    'Jack Sparrow', 'Kelly Clarkson', 'Liam Neeson', 'Monica Geller', 'Noah Webster'
  ];
  
  return names.map((name, index) => ({
    id: index + 1,
    name,
    score: Math.floor(Math.random() * 41) + 60, // Random score between 60-100%
    totalQuizzes: Math.floor(Math.random() * 5) + 8, // 8-12 total quizzes
    correctAnswers: 0,
    streak: Math.floor(Math.random() * 8) + 1,
    lastActive: ['Today', '1 day ago', '2 days ago', '3 days ago'][Math.floor(Math.random() * 4)],
    improvement: Math.floor(Math.random() * 21) - 10 // -10 to +10
  })).map(student => ({
    ...student,
    correctAnswers: Math.floor((student.score / 100) * student.totalQuizzes * 10)
  })).sort((a, b) => b.score - a.score);
};

const ClassLeaderboardPage: React.FC = () => {
  const [selectedFilter, setSelectedFilter] = useState('overall');
  const [selectedTimeframe, setSelectedTimeframe] = useState('semester');
  const [animateCards, setAnimateCards] = useState(false);
  const students = generateMockStudents();
  const classroomNumber = "Room 101-A";

  useEffect(() => {
    setAnimateCards(true);
  }, []);

  const filterOptions = [
    { value: 'overall', label: 'Overall Performance' },
    { value: 'quiz', label: 'Quiz Scores' },
    { value: 'participation', label: 'Participation' },
    { value: 'improvement', label: 'Most Improved' }
  ];

  const timeframeOptions = [
    { value: 'semester', label: 'This Semester' },
    { value: 'month', label: 'This Month' },
    { value: 'week', label: 'This Week' }
  ];

  const classAverage = Math.round(students.reduce((sum, s) => sum + s.score, 0) / students.length);
  const topScore = students[0]?.score || 0;
  const totalStudents = students.length;

  return (
    <div className="leaderboard-page modern-enhanced">
      {/* Background Effects */}
      <div className="background-decoration">
        <div className="floating-shapes">
          <div className="shape shape-1"></div>
          <div className="shape shape-2"></div>
          <div className="shape shape-3"></div>
        </div>
      </div>

      {/* Enhanced Header */}
      <div className={`leaderboard-header enhanced-header ${animateCards ? 'fade-in' : ''}`}>
        <div className="header-content">
          <div className="title-section">
            <h2 className="animated-title">
              <span className="title-icon">🏆</span>
              Class Leaderboard
            </h2>
            <div className="classroom-badge">
              <span className="badge-icon">📚</span>
              {classroomNumber}
            </div>
            <p className="subtitle">Weekly Quiz Performance Rankings</p>
          </div>
          
          {/* Filter Controls */}
          <div className="filter-controls">
            <div className="filter-group">
              <label>Performance Filter:</label>
              <select 
                value={selectedFilter} 
                onChange={(e) => setSelectedFilter(e.target.value)}
                className="modern-select"
                aria-label="Performance filter selection"
              >
                {filterOptions.map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>
            <div className="filter-group">
              <label>Time Period:</label>
              <select 
                value={selectedTimeframe} 
                onChange={(e) => setSelectedTimeframe(e.target.value)}
                className="modern-select"
                aria-label="Time period selection"
              >
                {timeframeOptions.map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>
        <div className="header-actions">
          <ThemeToggle />
          <UserButton />
        </div>
      </div>

      {/* Enhanced Stats Cards */}
      <div className={`leaderboard-stats enhanced-stats ${animateCards ? 'slide-in' : ''}`}>
        <div className="stat-card primary-stat">
          <div className="stat-icon">📊</div>
          <div className="stat-content">
            <h4>Class Average</h4>
            <p className="stat-value">{classAverage}%</p>
            <span className="stat-trend">+3.2% from last week</span>
          </div>
        </div>
        <div className="stat-card success-stat">
          <div className="stat-icon">⭐</div>
          <div className="stat-content">
            <h4>Top Score</h4>
            <p className="stat-value">{topScore}%</p>
            <span className="stat-trend">Excellent performance!</span>
          </div>
        </div>
        <div className="stat-card info-stat">
          <div className="stat-icon">👥</div>
          <div className="stat-content">
            <h4>Total Students</h4>
            <p className="stat-value">{totalStudents}</p>
            <span className="stat-trend">Active participants</span>
          </div>
        </div>
      </div>

      {/* Enhanced Leaderboard Table */}
      <div className={`leaderboard-table enhanced-table ${animateCards ? 'fade-in' : ''}`}>
        <div className="table-header modern-header">
          <div className="rank-col">
            <span className="header-icon">🥇</span>
            Rank
          </div>
          <div className="name-col">
            <span className="header-icon">👤</span>
            Student Name
          </div>
          <div className="score-col">
            <span className="header-icon">📈</span>
            Score %
          </div>
          <div className="quizzes-col">
            <span className="header-icon">📝</span>
            Quizzes
          </div>
          <div className="correct-col">
            <span className="header-icon">✅</span>
            Correct
          </div>
        </div>
        
        <div className="table-body modern-body">
          {students.map((student, index) => (
            <div 
              key={student.id} 
              className={`table-row enhanced-row ${index < 3 ? 'top-three' : ''} ${
                index === 0 ? 'first-place' : 
                index === 1 ? 'second-place' : 
                index === 2 ? 'third-place' : ''
              }`}
              data-delay={index}
            >
              <div className="rank-col">
                <div className="rank-badge">
                  {index === 0 && <span className="trophy gold">🥇</span>}
                  {index === 1 && <span className="trophy silver">🥈</span>}
                  {index === 2 && <span className="trophy bronze">🥉</span>}
                  {index > 2 && <span className="rank-number">{index + 1}</span>}
                </div>
              </div>
              <div className="name-col">
                <div className="student-info">
                  <span className="student-name">{student.name}</span>
                  <span className="student-meta">
                    Streak: {student.streak} • {student.lastActive}
                  </span>
                </div>
              </div>
              <div className="score-col">
                <div className="score-container">
                  <div className="score-bar modern-bar">
                    <div 
                      className="score-fill animated-fill progress-bar" 
                      data-score={student.score}
                    ></div>
                    <span className="score-text">{student.score}%</span>
                  </div>
                  <div className="improvement-indicator">
                    {student.improvement > 0 ? '📈' : student.improvement < 0 ? '📉' : '➖'}
                    <span className={`improvement-text ${
                      student.improvement > 0 ? 'positive' : 
                      student.improvement < 0 ? 'negative' : 'neutral'
                    }`}>
                      {student.improvement > 0 ? '+' : ''}{student.improvement}%
                    </span>
                  </div>
                </div>
              </div>
              <div className="quizzes-col">
                <div className="quiz-info">
                  <span className="quiz-count">{student.totalQuizzes}</span>
                  <span className="quiz-label">completed</span>
                </div>
              </div>
              <div className="correct-col">
                <div className="correct-info">
                  <span className="correct-count">{student.correctAnswers}</span>
                  <span className="correct-label">answers</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ClassLeaderboardPage;
