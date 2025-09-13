import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';


const ClassroomPage: React.FC = () => {
  const { code } = useParams<{ code: string }>();
  const navigate = useNavigate();
  const [teacher, setTeacher] = useState('');
  const [subject, setSubject] = useState('');
  const [day, setDay] = useState('');
  const [time, setTime] = useState('');
  return (
    <div className="classroom-page">
      <h2>Welcome to the Classroom</h2>
      <div className="classroom-form-row">
        <input
          className="classroom-input"
          type="text"
          placeholder="Enter Teacher Name"
          value={teacher}
          onChange={e => setTeacher(e.target.value)}
        />
        <input
          className="classroom-input"
          type="text"
          placeholder="Enter Subject Name"
          value={subject}
          onChange={e => setSubject(e.target.value)}
        />
        <input
          className="classroom-input"
          type="text"
          placeholder="Day"
          value={day}
          onChange={e => setDay(e.target.value)}
        />
        <input
          className="classroom-input"
          type="text"
          placeholder="Time"
          value={time}
          onChange={e => setTime(e.target.value)}
        />
      </div>
      <div className="classroom-options">
        <div className="classroom-option" onClick={() => navigate('attendance')}>
          Take Attendance
        </div>
        <div className="classroom-option" onClick={() => navigate('quiz')}>
          Generate Quiz
        </div>
        <div className="classroom-option" onClick={() => navigate('notes')}>
          Notes
        </div>
        <div className="classroom-option" onClick={() => navigate('leaderboard')}>
          Class Leaderboard
        </div>
      </div>
    </div>
  );
};

export default ClassroomPage;
