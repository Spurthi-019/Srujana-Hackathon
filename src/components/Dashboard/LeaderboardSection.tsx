import React, { useState } from 'react';

const LeaderboardSection: React.FC = () => {
  const [selectedMetric, setSelectedMetric] = useState('overall');
  const [selectedTimeframe, setSelectedTimeframe] = useState('semester');

  // Mock data for leaderboard
  const currentStudentRank = {
    overall: 3,
    attendance: 5,
    academic: 2,
    participation: 1,
    improvement: 4
  };

  const leaderboardData = [
    {
      rank: 1,
      name: 'Alice Johnson',
      avatar: '👩‍🎓',
      points: 2847,
      attendance: 98,
      gpa: 3.9,
      participation: 156,
      badges: ['🏆', '📚', '💬'],
      improvement: '+12%'
    },
    {
      rank: 2,
      name: 'Michael Chen',
      avatar: '👨‍🎓',
      points: 2756,
      attendance: 95,
      gpa: 3.8,
      participation: 142,
      badges: ['🥈', '📝', '🎯'],
      improvement: '+8%'
    },
    {
      rank: 3,
      name: 'You',
      avatar: '👤',
      points: 2698,
      attendance: 87,
      gpa: 3.7,
      participation: 124,
      badges: ['🥉', '💡', '📈'],
      improvement: '+15%',
      isCurrentUser: true
    },
    {
      rank: 4,
      name: 'Sarah Davis',
      avatar: '👩‍🎓',
      points: 2634,
      attendance: 92,
      gpa: 3.6,
      participation: 118,
      badges: ['⭐', '📊', '🤝'],
      improvement: '+5%'
    },
    {
      rank: 5,
      name: 'David Wilson',
      avatar: '👨‍🎓',
      points: 2578,
      attendance: 89,
      gpa: 3.5,
      participation: 109,
      badges: ['🎖️', '📋', '💭'],
      improvement: '+10%'
    }
  ];

  const achievements = [
    { title: 'Top 3 Overall', description: 'Ranked in top 3 students', icon: '🏆', achieved: true },
    { title: 'Participation King', description: '#1 in class participation', icon: '👑', achieved: true },
    { title: 'Consistency Award', description: '5 weeks in top 5', icon: '🎯', achieved: true },
    { title: 'Improvement Star', description: 'Biggest improvement this month', icon: '⭐', achieved: false }
  ];

  const weeklyProgress = [
    { week: 'Week 1', rank: 5, points: 2234 },
    { week: 'Week 2', rank: 4, points: 2367 },
    { week: 'Week 3', rank: 3, points: 2456 },
    { week: 'Week 4', rank: 3, points: 2578 },
    { week: 'Week 5', rank: 3, points: 2698 }
  ];

  const subjectRankings = [
    { subject: 'Mathematics', rank: 2, totalStudents: 28, trend: 'up' },
    { subject: 'Physics', rank: 4, totalStudents: 28, trend: 'same' },
    { subject: 'Chemistry', rank: 6, totalStudents: 28, trend: 'down' },
    { subject: 'Biology', rank: 1, totalStudents: 28, trend: 'up' },
    { subject: 'English', rank: 3, totalStudents: 28, trend: 'up' }
  ];

  const getRankColor = (rank: number) => {
    if (rank === 1) return 'rank-gold';
    if (rank === 2) return 'rank-silver';
    if (rank === 3) return 'rank-bronze';
    if (rank <= 5) return 'rank-top5';
    return 'rank-other';
  };

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'up': return '📈';
      case 'down': return '📉';
      case 'same': return '➡️';
      default: return '➡️';
    }
  };

  const getMetricDisplay = (metric: string, student: any) => {
    switch (metric) {
      case 'academic':
        return `${student.gpa} GPA`;
      case 'attendance':
        return `${student.attendance}%`;
      case 'participation':
        return `${student.participation} pts`;
      default:
        return `${student.points} pts`;
    }
  };

  return (
    <div className="leaderboard-section">
      {/* Rank Overview */}
      <div className="rank-overview">
        <div className="rank-card primary">
          <div className="rank-icon">🏆</div>
          <div className="rank-content">
            <h3>Overall Rank</h3>
            <div className="rank-number">#{currentStudentRank.overall}</div>
            <div className="rank-subtext">out of 28 students</div>
          </div>
        </div>

        <div className="rank-card">
          <div className="rank-icon">📅</div>
          <div className="rank-content">
            <h3>Attendance Rank</h3>
            <div className="rank-number">#{currentStudentRank.attendance}</div>
            <div className="rank-subtext">87% attendance</div>
          </div>
        </div>

        <div className="rank-card success">
          <div className="rank-icon">💬</div>
          <div className="rank-content">
            <h3>Participation Rank</h3>
            <div className="rank-number">#{currentStudentRank.participation}</div>
            <div className="rank-subtext">124 interactions</div>
          </div>
        </div>

        <div className="rank-card">
          <div className="rank-icon">📚</div>
          <div className="rank-content">
            <h3>Academic Rank</h3>
            <div className="rank-number">#{currentStudentRank.academic}</div>
            <div className="rank-subtext">3.7 GPA</div>
          </div>
        </div>
      </div>

      {/* Leaderboard Filters */}
      <div className="leaderboard-filters">
        <div className="filter-group">
          <label htmlFor="metric-select">Metric:</label>
          <select 
            id="metric-select"
            value={selectedMetric} 
            onChange={(e) => setSelectedMetric(e.target.value)}
            className="filter-select"
          >
            <option value="overall">Overall Score</option>
            <option value="academic">Academic Performance</option>
            <option value="attendance">Attendance</option>
            <option value="participation">Participation</option>
          </select>
        </div>

        <div className="filter-group">
          <label htmlFor="timeframe-select">Timeframe:</label>
          <select 
            id="timeframe-select"
            value={selectedTimeframe} 
            onChange={(e) => setSelectedTimeframe(e.target.value)}
            className="filter-select"
          >
            <option value="semester">This Semester</option>
            <option value="month">This Month</option>
            <option value="week">This Week</option>
          </select>
        </div>
      </div>

      {/* Main Leaderboard */}
      <div className="main-leaderboard">
        <h3>Class Leaderboard</h3>
        <div className="leaderboard-list">
          {leaderboardData.map((student, index) => (
            <div 
              key={index} 
              className={`leaderboard-item ${student.isCurrentUser ? 'current-user' : ''} ${getRankColor(student.rank)}`}
            >
              <div className="student-rank">#{student.rank}</div>
              <div className="student-avatar">{student.avatar}</div>
              <div className="student-info">
                <div className="student-name">{student.name}</div>
                <div className="student-badges">
                  {student.badges.map((badge, idx) => (
                    <span key={idx} className="badge">{badge}</span>
                  ))}
                </div>
              </div>
              <div className="student-stats">
                <div className="stat-item">
                  <span className="stat-value">{getMetricDisplay(selectedMetric, student)}</span>
                  <span className="stat-label">Score</span>
                </div>
                <div className="stat-item">
                  <span className="stat-value improvement">{student.improvement}</span>
                  <span className="stat-label">Growth</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Subject Rankings */}
      <div className="subject-rankings">
        <h3>Subject-wise Rankings</h3>
        <div className="rankings-grid">
          {subjectRankings.map((subject, index) => (
            <div key={index} className="ranking-card">
              <div className="ranking-header">
                <h4>{subject.subject}</h4>
                <div className="trend-indicator">
                  {getTrendIcon(subject.trend)}
                </div>
              </div>
              <div className="ranking-details">
                <div className={`rank-display ${getRankColor(subject.rank)}`}>
                  #{subject.rank}
                </div>
                <div className="rank-context">
                  out of {subject.totalStudents}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Progress Chart */}
      <div className="progress-chart">
        <h3>Weekly Progress</h3>
        <div className="chart-container">
          {weeklyProgress.map((week, index) => (
            <div key={index} className="progress-week">
              <div className="week-label">{week.week}</div>
              <div className="progress-bar">
                <div 
                  className="rank-indicator"
                  data-rank={week.rank}
                >
                  #{week.rank}
                </div>
              </div>
              <div className="points-label">{week.points} pts</div>
            </div>
          ))}
        </div>
      </div>

      {/* Achievements */}
      <div className="leaderboard-achievements">
        <h3>Ranking Achievements</h3>
        <div className="achievements-grid">
          {achievements.map((achievement, index) => (
            <div key={index} className={`achievement-card ${achievement.achieved ? 'achieved' : 'locked'}`}>
              <div className="achievement-icon">{achievement.icon}</div>
              <div className="achievement-content">
                <h4>{achievement.title}</h4>
                <p>{achievement.description}</p>
              </div>
              <div className="achievement-status">
                {achievement.achieved ? '✅' : '🔒'}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Competition Info */}
      <div className="competition-info">
        <h3>Upcoming Competitions</h3>
        <div className="competitions-list">
          <div className="competition-item">
            <div className="competition-icon">🏆</div>
            <div className="competition-details">
              <h4>Monthly Academic Challenge</h4>
              <p>Compete in quiz rounds across all subjects</p>
              <div className="competition-date">Starts: September 20, 2025</div>
            </div>
            <button className="join-btn">Join</button>
          </div>
          <div className="competition-item">
            <div className="competition-icon">🎯</div>
            <div className="competition-details">
              <h4>Attendance Challenge</h4>
              <p>Perfect attendance competition for October</p>
              <div className="competition-date">Starts: October 1, 2025</div>
            </div>
            <button className="join-btn">Join</button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LeaderboardSection;