import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import ClassroomPage from './ClassroomPage';
import StudentDashboard from './StudentDashboard';
import TeacherDashboard from './components/Teacher/TeacherDashboard';
import CreateClass from './components/Teacher/CreateClass';
import ClassConfirmation from './components/Teacher/ClassConfirmation';
import TakeAttendancePage from './TakeAttendancePage';
import AttendanceResultsPage from './AttendanceResultsPage';
import GenerateQuizPage from './GenerateQuizPage';
import TakeNotesPage from './TakeNotesPage';
import ClassLeaderboardPage from './ClassLeaderboardPage';
import ProtectedRoute from './components/ProtectedRoute';
import ToastContainer from './components/ToastContainer';
import reportWebVitals from './reportWebVitals';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from './contexts/ThemeContext';
import { ToastProvider } from './contexts/ToastContext';
import { ClerkProvider } from '@clerk/clerk-react';

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
                  <TakeNotesPage />
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
