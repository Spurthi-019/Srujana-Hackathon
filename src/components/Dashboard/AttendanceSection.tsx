import React, { useState } from 'react';

const AttendanceSection: React.FC = () => {
  const [selectedMonth, setSelectedMonth] = useState('current');

  // Mock data for attendance
  const attendanceData = {
    overall: 87,
    thisMonth: 92,
    lastMonth: 85,
    thisWeek: 100,
    totalClasses: 45,
    attendedClasses: 39,
    absentDays: 6
  };

  const weeklyAttendance = [
    { day: 'Mon', attended: true, subject: 'Math' },
    { day: 'Tue', attended: true, subject: 'Physics' },
    { day: 'Wed', attended: false, subject: 'Chemistry' },
    { day: 'Thu', attended: true, subject: 'Biology' },
    { day: 'Fri', attended: true, subject: 'English' }
  ];

  const monthlyTrend = [
    { month: 'Sep', percentage: 92 },
    { month: 'Aug', percentage: 85 },
    { month: 'Jul', percentage: 88 },
    { month: 'Jun', percentage: 90 },
    { month: 'May', percentage: 82 },
    { month: 'Apr', percentage: 94 }
  ];

  const recentAbsences = [
    { date: '2025-09-10', subject: 'Chemistry', reason: 'Sick leave', status: 'Excused' },
    { date: '2025-09-05', subject: 'Math', reason: 'Family emergency', status: 'Excused' },
    { date: '2025-08-28', subject: 'Physics', reason: 'Unexcused', status: 'Unexcused' }
  ];

  return (
    <div className="attendance-section">
      {/* Attendance Overview Cards */}
      <div className="attendance-overview">
        <div className="attendance-stat-card primary">
          <div className="stat-icon">📊</div>
          <div className="stat-content">
            <h3>Overall Attendance</h3>
            <div className="percentage-display">{attendanceData.overall}%</div>
            <div className="stat-subtext">{attendanceData.attendedClasses}/{attendanceData.totalClasses} classes</div>
          </div>
        </div>

        <div className="attendance-stat-card">
          <div className="stat-icon">📅</div>
          <div className="stat-content">
            <h3>This Month</h3>
            <div className="percentage-display">{attendanceData.thisMonth}%</div>
            <div className="stat-subtext">Great improvement!</div>
          </div>
        </div>

        <div className="attendance-stat-card">
          <div className="stat-icon">⏰</div>
          <div className="stat-content">
            <h3>This Week</h3>
            <div className="percentage-display">{attendanceData.thisWeek}%</div>
            <div className="stat-subtext">Perfect week!</div>
          </div>
        </div>

        <div className="attendance-stat-card warning">
          <div className="stat-icon">⚠️</div>
          <div className="stat-content">
            <h3>Absent Days</h3>
            <div className="percentage-display">{attendanceData.absentDays}</div>
            <div className="stat-subtext">Total this semester</div>
          </div>
        </div>
      </div>

      {/* Weekly Attendance */}
      <div className="weekly-attendance">
        <h3>This Week's Attendance</h3>
        <div className="week-grid">
          {weeklyAttendance.map((day, index) => (
            <div key={index} className={`day-card ${day.attended ? 'present' : 'absent'}`}>
              <div className="day-name">{day.day}</div>
              <div className="attendance-status">
                {day.attended ? '✅' : '❌'}
              </div>
              <div className="subject-name">{day.subject}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Attendance Trend Chart */}
      <div className="attendance-trend">
        <div className="trend-header">
          <h3>Attendance Trend</h3>
          <select 
            value={selectedMonth} 
            onChange={(e) => setSelectedMonth(e.target.value)}
            className="month-selector"
          >
            <option value="current">Last 6 Months</option>
            <option value="semester">This Semester</option>
            <option value="year">This Year</option>
          </select>
        </div>
        <div className="trend-chart">
          {monthlyTrend.map((data, index) => (
            <div key={index} className="chart-bar">
              <div 
                className="bar-fill"
                style={{ height: `${data.percentage}%` }}
              ></div>
              <div className="bar-label">{data.month}</div>
              <div className="bar-percentage">{data.percentage}%</div>
            </div>
          ))}
        </div>
      </div>

      {/* Recent Absences */}
      <div className="recent-absences">
        <h3>Recent Absences</h3>
        <div className="absences-list">
          {recentAbsences.map((absence, index) => (
            <div key={index} className="absence-item">
              <div className="absence-date">{absence.date}</div>
              <div className="absence-subject">{absence.subject}</div>
              <div className="absence-reason">{absence.reason}</div>
              <div className={`absence-status ${absence.status.toLowerCase()}`}>
                {absence.status}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Attendance Goals */}
      <div className="attendance-goals">
        <h3>Attendance Goals</h3>
        <div className="goals-grid">
          <div className="goal-card">
            <div className="goal-title">Monthly Target</div>
            <div className="goal-progress">
              <div className="progress-bar">
                <div 
                  className="progress-fill"
                  style={{ width: `${(attendanceData.thisMonth / 95) * 100}%` }}
                ></div>
              </div>
              <div className="goal-text">{attendanceData.thisMonth}% / 95%</div>
            </div>
          </div>

          <div className="goal-card">
            <div className="goal-title">Semester Target</div>
            <div className="goal-progress">
              <div className="progress-bar">
                <div 
                  className="progress-fill"
                  style={{ width: `${(attendanceData.overall / 90) * 100}%` }}
                ></div>
              </div>
              <div className="goal-text">{attendanceData.overall}% / 90%</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AttendanceSection;