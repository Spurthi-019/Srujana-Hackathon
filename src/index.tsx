import ReactDOM from 'react-dom/client';
import './index.css';

// Simple test component
function TestApp() {
  return (
    <div style={{ 
      padding: '20px', 
      textAlign: 'center', 
      fontFamily: 'Arial',
      backgroundColor: 'white',
      minHeight: '100vh',
      color: 'black'
    }}>
      <h1 style={{ color: 'blue' }}>ClassTrack - Loading Test</h1>
      <p>If you can see this, the deployment is working!</p>
      <p>Current time: {new Date().toLocaleString()}</p>
      <button onClick={() => alert('Button works!')}>Test Button</button>
    </div>
  );
}

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);

root.render(<TestApp />);
