import React, { useState } from 'react';

const InteractionsSection: React.FC = () => {
  const [selectedTimeframe, setSelectedTimeframe] = useState('week');

  // Mock data for class interactions
  const interactionStats = {
    totalInteractions: 124,
    thisWeek: 24,
    questionsAsked: 18,
    answersGiven: 31,
    participationScore: 8.7,
    rank: 3
  };

  const weeklyInteractions = [
    { day: 'Monday', questions: 3, answers: 2, participation: 4 },
    { day: 'Tuesday', questions: 2, answers: 4, participation: 5 },
    { day: 'Wednesday', questions: 1, answers: 3, participation: 3 },
    { day: 'Thursday', questions: 4, answers: 2, participation: 6 },
    { day: 'Friday', questions: 2, answers: 5, participation: 4 }
  ];

  const recentQuestions = [
    {
      subject: 'Mathematics',
      question: 'How do we solve integration by parts when the function is complex?',
      timestamp: '2025-09-12 10:30 AM',
      answers: 3,
      likes: 5,
      resolved: true
    },
    {
      subject: 'Physics',
      question: 'What is the relationship between wavelength and frequency in electromagnetic waves?',
      timestamp: '2025-09-11 2:15 PM',
      answers: 2,
      likes: 8,
      resolved: true
    },
    {
      subject: 'Chemistry',
      question: 'Can someone explain the mechanism of SN2 reactions?',
      timestamp: '2025-09-10 11:45 AM',
      answers: 4,
      likes: 6,
      resolved: false
    }
  ];

  const classParticipation = [
    {
      subject: 'Mathematics',
      sessions: 12,
      participated: 10,
      percentage: 83,
      lastActivity: 'Asked about derivatives',
      activityType: 'question'
    },
    {
      subject: 'Physics',
      sessions: 10,
      participated: 9,
      percentage: 90,
      lastActivity: 'Answered wave equation',
      activityType: 'answer'
    },
    {
      subject: 'Chemistry',
      sessions: 8,
      participated: 6,
      percentage: 75,
      lastActivity: 'Discussed bond angles',
      activityType: 'discussion'
    },
    {
      subject: 'Biology',
      sessions: 9,
      participated: 8,
      percentage: 89,
      lastActivity: 'Presented on mitosis',
      activityType: 'presentation'
    }
  ];

  const achievements = [
    { title: 'Question Master', description: 'Asked 10+ meaningful questions this week', icon: '❓', earned: true },
    { title: 'Helper', description: 'Answered 15+ classmate questions', icon: '🤝', earned: true },
    { title: 'Active Participant', description: 'Participated in all classes this week', icon: '🎯', earned: true },
    { title: 'Discussion Leader', description: 'Led 3+ class discussions', icon: '💬', earned: false }
  ];

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'question': return '❓';
      case 'answer': return '💡';
      case 'discussion': return '💬';
      case 'presentation': return '📽️';
      default: return '📝';
    }
  };

  const getParticipationColor = (percentage: number) => {
    if (percentage >= 85) return 'excellent';
    if (percentage >= 70) return 'good';
    if (percentage >= 50) return 'average';
    return 'poor';
  };

  return (
    <div className="interactions-section">
      {/* Interaction Overview */}
      <div className="interaction-overview">
        <div className="interaction-stat-card primary">
          <div className="stat-icon">💬</div>
          <div className="stat-content">
            <h3>Total Interactions</h3>
            <div className="stat-number">{interactionStats.totalInteractions}</div>
            <div className="stat-subtext">This semester</div>
          </div>
        </div>

        <div className="interaction-stat-card">
          <div className="stat-icon">❓</div>
          <div className="stat-content">
            <h3>Questions Asked</h3>
            <div className="stat-number">{interactionStats.questionsAsked}</div>
            <div className="stat-subtext">This week</div>
          </div>
        </div>

        <div className="interaction-stat-card">
          <div className="stat-icon">💡</div>
          <div className="stat-content">
            <h3>Answers Given</h3>
            <div className="stat-number">{interactionStats.answersGiven}</div>
            <div className="stat-subtext">This week</div>
          </div>
        </div>

        <div className="interaction-stat-card success">
          <div className="stat-icon">⭐</div>
          <div className="stat-content">
            <h3>Participation Score</h3>
            <div className="stat-number">{interactionStats.participationScore}/10</div>
            <div className="stat-subtext">Rank #{interactionStats.rank} in class</div>
          </div>
        </div>
      </div>

      {/* Weekly Activity Chart */}
      <div className="weekly-activity">
        <div className="activity-header">
          <h3>Weekly Activity</h3>
          <select 
            value={selectedTimeframe} 
            onChange={(e) => setSelectedTimeframe(e.target.value)}
            className="timeframe-selector"
            title="Select timeframe"
          >
            <option value="week">This Week</option>
            <option value="month">This Month</option>
            <option value="semester">This Semester</option>
          </select>
        </div>

        <div className="activity-chart">
          {weeklyInteractions.map((day, index) => (
            <div key={index} className="activity-day">
              <div className="day-name">{day.day}</div>
              <div className="activity-bars">
                <div className="activity-bar questions" data-value={day.questions}>
                  <div className="bar-fill"></div>
                  <span className="bar-label">Q: {day.questions}</span>
                </div>
                <div className="activity-bar answers" data-value={day.answers}>
                  <div className="bar-fill"></div>
                  <span className="bar-label">A: {day.answers}</span>
                </div>
                <div className="activity-bar participation" data-value={day.participation}>
                  <div className="bar-fill"></div>
                  <span className="bar-label">P: {day.participation}</span>
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="chart-legend">
          <div className="legend-item">
            <div className="legend-color questions"></div>
            <span>Questions Asked</span>
          </div>
          <div className="legend-item">
            <div className="legend-color answers"></div>
            <span>Answers Given</span>
          </div>
          <div className="legend-item">
            <div className="legend-color participation"></div>
            <span>Participation Points</span>
          </div>
        </div>
      </div>

      {/* Recent Questions */}
      <div className="recent-questions">
        <h3>Recent Questions</h3>
        <div className="questions-list">
          {recentQuestions.map((item, index) => (
            <div key={index} className="question-item">
              <div className="question-header">
                <div className="question-subject">{item.subject}</div>
                <div className="question-timestamp">{item.timestamp}</div>
                <div className={`question-status ${item.resolved ? 'resolved' : 'pending'}`}>
                  {item.resolved ? '✅ Resolved' : '⏳ Pending'}
                </div>
              </div>
              <div className="question-content">{item.question}</div>
              <div className="question-stats">
                <span className="stat-item">👥 {item.answers} answers</span>
                <span className="stat-item">👍 {item.likes} likes</span>
                <button className="view-details-btn">View Details</button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Class Participation */}
      <div className="class-participation">
        <h3>Subject-wise Participation</h3>
        <div className="participation-grid">
          {classParticipation.map((subject, index) => (
            <div key={index} className="participation-card">
              <div className="participation-header">
                <h4>{subject.subject}</h4>
                <div className={`participation-badge ${getParticipationColor(subject.percentage)}`}>
                  {subject.percentage}%
                </div>
              </div>
              <div className="participation-details">
                <div className="detail-row">
                  <span>Sessions participated:</span>
                  <span>{subject.participated}/{subject.sessions}</span>
                </div>
                <div className="detail-row">
                  <span>Last activity:</span>
                  <span className="activity-detail">
                    {getActivityIcon(subject.activityType)} {subject.lastActivity}
                  </span>
                </div>
              </div>
              <div className="participation-progress">
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

      {/* Achievements */}
      <div className="achievements">
        <h3>Interaction Achievements</h3>
        <div className="achievements-grid">
          {achievements.map((achievement, index) => (
            <div key={index} className={`achievement-card ${achievement.earned ? 'earned' : 'locked'}`}>
              <div className="achievement-icon">{achievement.icon}</div>
              <div className="achievement-content">
                <h4>{achievement.title}</h4>
                <p>{achievement.description}</p>
              </div>
              <div className="achievement-status">
                {achievement.earned ? '✅' : '🔒'}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="quick-actions">
        <h3>Quick Actions</h3>
        <div className="actions-grid">
          <button className="action-card">
            <div className="action-icon">❓</div>
            <div className="action-text">Ask Question</div>
          </button>
          <button className="action-card">
            <div className="action-icon">💡</div>
            <div className="action-text">Browse Questions</div>
          </button>
          <button className="action-card">
            <div className="action-icon">📊</div>
            <div className="action-text">View Analytics</div>
          </button>
          <button className="action-card">
            <div className="action-icon">🎯</div>
            <div className="action-text">Set Goals</div>
          </button>
        </div>
      </div>
    </div>
  );
};

export default InteractionsSection;