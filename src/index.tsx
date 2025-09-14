import { ClerkProvider } from '@clerk/clerk-react';
import React, { Suspense, lazy } from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter, Route, Routes } from 'react-router-dom';
import App from './App';
import LoadingSpinner from './components/LoadingSpinner';
import ProtectedRoute from './components/ProtectedRoute';
import ToastContainer from './components/ToastContainer';
import { ThemeProvider } from './contexts/ThemeContext';
import { ToastProvider } from './contexts/ToastContext';
import './index.css';
import reportWebVitals from './reportWebVitals';

// Lazy load components to reduce initial bundle size
const StudentDashboard = lazy(() => import('./StudentDashboard'));
const TeacherDashboard = lazy(() => import('./components/Teacher/TeacherDashboard'));
const CreateClass = lazy(() => import('./components/Teacher/CreateClass'));
const ClassConfirmation = lazy(() => import('./components/Teacher/ClassConfirmation'));
const ClassroomPage = lazy(() => import('./ClassroomPage'));
const TakeAttendancePage = lazy(() => import('./TakeAttendancePage'));
const AttendanceResultsPage = lazy(() => import('./AttendanceResultsPage'));
const GenerateQuizPage = lazy(() => import('./GenerateQuizPage'));
const ClassNotes = lazy(() => import('./components/ClassNotes'));
const ClassLeaderboardPage = lazy(() => import('./ClassLeaderboardPage'));

// Import your Publishable Key with fallback for development
const PUBLISHABLE_KEY = process.env.REACT_APP_CLERK_PUBLISHABLE_KEY || 'pk_test_demo_key_placeholder';

if (!process.env.REACT_APP_CLERK_PUBLISHABLE_KEY) {
  console.warn('Clerk Publishable Key not found. Using demo key for development.');
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
                  <Suspense fallback={<LoadingSpinner />}>
                    <StudentDashboard />
                  </Suspense>
                </ProtectedRoute>
              } />
              <Route path="/teacher/dashboard" element={
                <ProtectedRoute>
                  <Suspense fallback={<LoadingSpinner />}>
                    <TeacherDashboard />
                  </Suspense>
                </ProtectedRoute>
              } />
              <Route path="/teacher/create-class" element={
                <ProtectedRoute>
                  <Suspense fallback={<LoadingSpinner />}>
                    <CreateClass />
                  </Suspense>
                </ProtectedRoute>
              } />
              <Route path="/teacher/class-confirmation" element={
                <ProtectedRoute>
                  <Suspense fallback={<LoadingSpinner />}>
                    <ClassConfirmation />
                  </Suspense>
                </ProtectedRoute>
              } />
              <Route path="/classroom/:code" element={
                <ProtectedRoute>
                  <Suspense fallback={<LoadingSpinner />}>
                    <ClassroomPage />
                  </Suspense>
                </ProtectedRoute>
              } />
              <Route path="/classroom/:code/attendance" element={
                <ProtectedRoute>
                  <Suspense fallback={<LoadingSpinner />}>
                    <TakeAttendancePage />
                  </Suspense>
                </ProtectedRoute>
              } />
              <Route path="/classroom/:code/attendance/results" element={
                <ProtectedRoute>
                  <Suspense fallback={<LoadingSpinner />}>
                    <AttendanceResultsPage />
                  </Suspense>
                </ProtectedRoute>
              } />
              <Route path="/classroom/:code/quiz" element={
                <ProtectedRoute>
                  <Suspense fallback={<LoadingSpinner />}>
                    <GenerateQuizPage />
                  </Suspense>
                </ProtectedRoute>
              } />
              <Route path="/classroom/:code/notes" element={
                <ProtectedRoute>
                  <Suspense fallback={<LoadingSpinner />}>
                    <ClassNotes />
                  </Suspense>
                </ProtectedRoute>
              } />
              <Route path="/classroom/:code/leaderboard" element={
                <ProtectedRoute>
                  <Suspense fallback={<LoadingSpinner />}>
                    <ClassLeaderboardPage />
                  </Suspense>
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
