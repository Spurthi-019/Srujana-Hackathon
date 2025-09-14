import { ClerkProvider } from '@clerk/clerk-react';
import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter, Route, Routes } from 'react-router-dom';
import App from './App';
import AttendanceResultsPage from './AttendanceResultsPage';
import ClassLeaderboardPage from './ClassLeaderboardPage';
import ClassroomPage from './ClassroomPage';
import GenerateQuizPage from './GenerateQuizPage';
import StudentDashboard from './StudentDashboard';
import TakeAttendancePage from './TakeAttendancePage';
import ClassNotes from './components/ClassNotes';
import ProtectedRoute from './components/ProtectedRoute';
import ClassConfirmation from './components/Teacher/ClassConfirmation';
import CreateClass from './components/Teacher/CreateClass';
import TeacherDashboard from './components/Teacher/TeacherDashboard';
import ToastContainer from './components/ToastContainer';
import { ThemeProvider } from './contexts/ThemeContext';
import { ToastProvider } from './contexts/ToastContext';
import './index.css';
import reportWebVitals from './reportWebVitals';

// Import your Publishable Key
const PUBLISHABLE_KEY = process.env.REACT_APP_CLERK_PUBLISHABLE_KEY;

if (!PUBLISHABLE_KEY) {
  throw new Error('Add your Clerk Publishable Key to the .env file');
}

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);

root.render(
  <React.StrictMode>
    <ClerkProvider publishableKey={PUBLISHABLE_KEY}>
      <ToastProvider>
        <ThemeProvider>
          <BrowserRouter>
            <Routes>
              <Route path="/" element={<App />} />
              <Route path="/student/dashboard" element={
                <ProtectedRoute>
                  <StudentDashboard />
                </ProtectedRoute>
              } />
              <Route path="/teacher/dashboard" element={
                <ProtectedRoute>
                  <TeacherDashboard />
                </ProtectedRoute>
              } />
              <Route path="/teacher/create-class" element={
                <ProtectedRoute>
                  <CreateClass />
                </ProtectedRoute>
              } />
              <Route path="/teacher/class-confirmation" element={
                <ProtectedRoute>
                  <ClassConfirmation />
                </ProtectedRoute>
              } />
              <Route path="/classroom/:code" element={
                <ProtectedRoute>
                  <ClassroomPage />
                </ProtectedRoute>
              } />
              <Route path="/classroom/:code/attendance" element={
                <ProtectedRoute>
                  <TakeAttendancePage />
                </ProtectedRoute>
              } />
              <Route path="/classroom/:code/attendance/results" element={
                <ProtectedRoute>
                  <AttendanceResultsPage />
                </ProtectedRoute>
              } />
              <Route path="/classroom/:code/quiz" element={
                <ProtectedRoute>
                  <GenerateQuizPage />
                </ProtectedRoute>
              } />
              <Route path="/classroom/:code/notes" element={
                <ProtectedRoute>
                  <ClassNotes />
                </ProtectedRoute>
              } />
              <Route path="/classroom/:code/leaderboard" element={
                <ProtectedRoute>
                  <ClassLeaderboardPage />
                </ProtectedRoute>
              } />
            </Routes>
            <ToastContainer />
          </BrowserRouter>
        </ThemeProvider>
      </ToastProvider>
    </ClerkProvider>
  </React.StrictMode>
);

reportWebVitals();
