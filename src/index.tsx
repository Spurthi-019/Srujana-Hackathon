import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import ClassroomPage from './ClassroomPage';
import LoginPage from './LoginPage';
import SignUpPage from './SignUpPage';
import TakeAttendancePage from './TakeAttendancePage';
import GenerateQuizPage from './GenerateQuizPage';
import TakeNotesPage from './TakeNotesPage';
import ClassLeaderboardPage from './ClassLeaderboardPage';
import reportWebVitals from './reportWebVitals';
import { BrowserRouter, Routes, Route } from 'react-router-dom';

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);
root.render(
  <React.StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<App />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/signup" element={<SignUpPage />} />
        <Route path="/classroom/:code" element={<ClassroomPage />} >
          <Route path="attendance" element={<TakeAttendancePage />} />
          <Route path="quiz" element={<GenerateQuizPage />} />
          <Route path="notes" element={<TakeNotesPage />} />
          <Route path="leaderboard" element={<ClassLeaderboardPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  </React.StrictMode>
);

reportWebVitals();
