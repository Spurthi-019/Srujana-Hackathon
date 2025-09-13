import React from 'react';
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
    correctAnswers: 0
  })).map(student => ({
    ...student,
    correctAnswers: Math.floor((student.score / 100) * student.totalQuizzes * 10)
  })).sort((a, b) => b.score - a.score);
};

const ClassLeaderboardPage: React.FC = () => {
  const students = generateMockStudents();
  const classroomNumber = "Room 101-A";

  return (
    <div className="leaderboard-page">
      <div className="leaderboard-header">
        <div className="header-content">
          <h2>Class Leaderboard</h2>
          <h3>Classroom: {classroomNumber}</h3>
          <p>Friday Results - Weekly Quiz Performance</p>
        </div>
        <ThemeToggle />
      </div>
      
      <div className="leaderboard-table">
        <div className="table-header">
          <div className="rank-col">Rank</div>
          <div className="name-col">Student Name</div>
          <div className="score-col">Score %</div>
          <div className="quizzes-col">Total Quizzes</div>
          <div className="correct-col">Correct Answers</div>
        </div>
        
        <div className="table-body">
          {students.map((student, index) => (
            <div 
              key={student.id} 
              className={`table-row ${index < 3 ? 'top-three' : ''} ${index === 0 ? 'first-place' : index === 1 ? 'second-place' : index === 2 ? 'third-place' : ''}`}
            >
              <div className="rank-col">
                {index === 0 && '🥇'}
                {index === 1 && '🥈'}
                {index === 2 && '🥉'}
                {index > 2 && (index + 1)}
              </div>
              <div className="name-col">{student.name}</div>
              <div className="score-col">
                <div className="score-bar">
                  <div 
                    className="score-fill" 
                    data-score={student.score}
                  ></div>
                  <span className="score-text">{student.score}%</span>
                </div>
              </div>
              <div className="quizzes-col">{student.totalQuizzes}</div>
              <div className="correct-col">{student.correctAnswers}</div>
            </div>
          ))}
        </div>
      </div>
      
      <div className="leaderboard-stats">
        <div className="stat-card">
          <h4>Class Average</h4>
          <p>{Math.round(students.reduce((sum, s) => sum + s.score, 0) / students.length)}%</p>
        </div>
        <div className="stat-card">
          <h4>Top Score</h4>
          <p>{students[0]?.score}%</p>
        </div>
        <div className="stat-card">
          <h4>Total Students</h4>
          <p>{students.length}</p>
        </div>
      </div>
    </div>
  );
};

export default ClassLeaderboardPage;
