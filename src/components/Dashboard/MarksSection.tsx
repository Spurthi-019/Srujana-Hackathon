import React, { useState } from 'react';

const MarksSection: React.FC = () => {
  const [selectedSubject, setSelectedSubject] = useState('all');

  // Mock data for marks and grades
  const academicData = {
    overallGPA: 3.7,
    currentGrade: 'A-',
    improvement: '+0.2',
    totalAssignments: 24,
    completedAssignments: 22,
    averageScore: 87
  };

  const subjectGrades = [
    { subject: 'Mathematics', grade: 'A', percentage: 92, credits: 4, lastTest: 89 },
    { subject: 'Physics', grade: 'A-', percentage: 88, credits: 4, lastTest: 85 },
    { subject: 'Chemistry', grade: 'B+', percentage: 85, credits: 3, lastTest: 82 },
    { subject: 'Biology', grade: 'A', percentage: 91, credits: 3, lastTest: 94 },
    { subject: 'English', grade: 'A-', percentage: 87, credits: 2, lastTest: 90 }
  ];

  const recentQuizzes = [
    { subject: 'Mathematics', topic: 'Calculus Integration', score: 89, maxScore: 100, date: '2025-09-12' },
    { subject: 'Physics', topic: 'Electromagnetic Waves', score: 85, maxScore: 100, date: '2025-09-10' },
    { subject: 'Chemistry', topic: 'Organic Reactions', score: 82, maxScore: 100, date: '2025-09-08' },
    { subject: 'Biology', topic: 'Cell Division', score: 94, maxScore: 100, date: '2025-09-06' }
  ];

  const performanceTrend = [
    { month: 'Apr', score: 82 },
    { month: 'May', score: 85 },
    { month: 'Jun', score: 87 },
    { month: 'Jul', score: 89 },
    { month: 'Aug', score: 86 },
    { month: 'Sep', score: 87 }
  ];

  const upcomingAssignments = [
    { subject: 'Mathematics', title: 'Differential Equations Assignment', dueDate: '2025-09-20', weightage: '15%' },
    { subject: 'Physics', title: 'Lab Report - Optics', dueDate: '2025-09-22', weightage: '10%' },
    { subject: 'Chemistry', title: 'Research Project', dueDate: '2025-09-25', weightage: '20%' }
  ];

  const getGradeColor = (grade: string) => {
    if (grade.startsWith('A')) return 'grade-a';
    if (grade.startsWith('B')) return 'grade-b';
    if (grade.startsWith('C')) return 'grade-c';
    return 'grade-d';
  };

  const getScoreColor = (score: number) => {
    if (score >= 90) return 'score-excellent';
    if (score >= 80) return 'score-good';
    if (score >= 70) return 'score-average';
    return 'score-poor';
  };

  return (
    <div className="marks-section">
      {/* Academic Overview */}
      <div className="academic-overview">
        <div className="academic-stat-card primary">
          <div className="stat-icon">🎯</div>
          <div className="stat-content">
            <h3>Overall GPA</h3>
            <div className="gpa-display">{academicData.overallGPA}</div>
            <div className="stat-subtext">Current Grade: {academicData.currentGrade}</div>
          </div>
        </div>

        <div className="academic-stat-card success">
          <div className="stat-icon">📈</div>
          <div className="stat-content">
            <h3>Improvement</h3>
            <div className="improvement-display">{academicData.improvement}</div>
            <div className="stat-subtext">Since last semester</div>
          </div>
        </div>

        <div className="academic-stat-card">
          <div className="stat-icon">📋</div>
          <div className="stat-content">
            <h3>Assignments</h3>
            <div className="assignment-display">{academicData.completedAssignments}/{academicData.totalAssignments}</div>
            <div className="stat-subtext">Completed this semester</div>
          </div>
        </div>

        <div className="academic-stat-card">
          <div className="stat-icon">⭐</div>
          <div className="stat-content">
            <h3>Average Score</h3>
            <div className="score-display">{academicData.averageScore}%</div>
            <div className="stat-subtext">Across all subjects</div>
          </div>
        </div>
      </div>

      {/* Subject-wise Grades */}
      <div className="subject-grades">
        <div className="section-header">
          <h3>Subject-wise Performance</h3>
          <select 
            value={selectedSubject} 
            onChange={(e) => setSelectedSubject(e.target.value)}
            className="subject-filter"
            title="Filter by subject"
          >
            <option value="all">All Subjects</option>
            {subjectGrades.map((subject, index) => (
              <option key={index} value={subject.subject}>{subject.subject}</option>
            ))}
          </select>
        </div>

        <div className="grades-grid">
          {subjectGrades
            .filter(subject => selectedSubject === 'all' || subject.subject === selectedSubject)
            .map((subject, index) => (
            <div key={index} className="grade-card">
              <div className="grade-header">
                <h4>{subject.subject}</h4>
                <div className={`grade-badge ${getGradeColor(subject.grade)}`}>
                  {subject.grade}
                </div>
              </div>
              <div className="grade-details">
                <div className="detail-item">
                  <span className="detail-label">Percentage:</span>
                  <span className="detail-value">{subject.percentage}%</span>
                </div>
                <div className="detail-item">
                  <span className="detail-label">Credits:</span>
                  <span className="detail-value">{subject.credits}</span>
                </div>
                <div className="detail-item">
                  <span className="detail-label">Last Test:</span>
                  <span className={`detail-value ${getScoreColor(subject.lastTest)}`}>
                    {subject.lastTest}%
                  </span>
                </div>
              </div>
              <div className="grade-progress">
                <div className="progress-bar">
                  <div 
                    className="progress-fill"
                    data-percentage={subject.percentage}
                  ></div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Recent Quizzes */}
      <div className="recent-quizzes">
        <h3>Recent Quiz Scores</h3>
        <div className="quizzes-list">
          {recentQuizzes.map((quiz, index) => (
            <div key={index} className="quiz-item">
              <div className="quiz-info">
                <div className="quiz-subject">{quiz.subject}</div>
                <div className="quiz-topic">{quiz.topic}</div>
                <div className="quiz-date">{quiz.date}</div>
              </div>
              <div className="quiz-score">
                <div className={`score-value ${getScoreColor(quiz.score)}`}>
                  {quiz.score}/{quiz.maxScore}
                </div>
                <div className="score-percentage">
                  {Math.round((quiz.score / quiz.maxScore) * 100)}%
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Performance Trend */}
      <div className="performance-trend">
        <h3>Performance Trend</h3>
        <div className="trend-chart">
          {performanceTrend.map((data, index) => (
            <div key={index} className="chart-column">
              <div 
                className="column-bar"
                data-score={data.score}
              ></div>
              <div className="column-label">{data.month}</div>
              <div className="column-score">{data.score}%</div>
            </div>
          ))}
        </div>
      </div>

      {/* Upcoming Assignments */}
      <div className="upcoming-assignments">
        <h3>Upcoming Assignments</h3>
        <div className="assignments-list">
          {upcomingAssignments.map((assignment, index) => (
            <div key={index} className="assignment-item">
              <div className="assignment-info">
                <div className="assignment-title">{assignment.title}</div>
                <div className="assignment-subject">{assignment.subject}</div>
              </div>
              <div className="assignment-details">
                <div className="assignment-due">Due: {assignment.dueDate}</div>
                <div className="assignment-weight">Weight: {assignment.weightage}</div>
              </div>
              <div className="assignment-actions">
                <button className="action-btn primary">Start</button>
                <button className="action-btn secondary">Details</button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default MarksSection;