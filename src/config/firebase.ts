// Firebase configuration for frontend
export const firebaseConfig = {
  apiKey: process.env.REACT_APP_FIREBASE_API_KEY || "AIzaSyC7BIZS3a-nQ_4mIduiGKTgufYND6_Y0Uc",
  authDomain: process.env.REACT_APP_FIREBASE_AUTH_DOMAIN,
  projectId: process.env.REACT_APP_FIREBASE_PROJECT_ID,
  storageBucket: process.env.REACT_APP_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: process.env.REACT_APP_FIREBASE_MESSAGING_SENDER_ID,
  appId: process.env.REACT_APP_FIREBASE_APP_ID
};

// Check if Firebase is properly configured
export const isFirebaseConfigured = () => {
  return firebaseConfig.apiKey && firebaseConfig.apiKey !== "your-api-key-here";
};