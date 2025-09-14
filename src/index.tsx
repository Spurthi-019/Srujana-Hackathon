import ReactDOM from 'react-dom/client';

// ClassTrack App with inline styles to avoid CSS conflicts
function ClassTrackApp() {
  return (
    <div style={{ 
      padding: '20px', 
      fontFamily: 'system-ui, -apple-system, sans-serif',
      backgroundColor: 'white',
      minHeight: '100vh',
      color: '#333',
      position: 'relative',
      zIndex: 10
    }}>
      <header style={{ textAlign: 'center', marginBottom: '40px' }}>
        <h1 style={{ 
          color: '#667eea', 
          marginBottom: '10px',
          fontSize: '2.5rem',
          fontWeight: 'bold'
        }}>
          ClassTrack
        </h1>
        <p style={{ 
          color: '#666',
          fontSize: '1.2rem'
        }}>
          Smart Classroom Management System
        </p>
      </header>

      <main style={{ maxWidth: '1000px', margin: '0 auto' }}>
        <div style={{ 
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', 
          padding: '40px', 
          borderRadius: '15px',
          textAlign: 'center',
          color: 'white',
          marginBottom: '40px'
        }}>
          <h2 style={{ marginBottom: '20px', fontSize: '2rem' }}>Welcome to ClassTrack</h2>
          <p style={{ fontSize: '1.1rem', marginBottom: '30px' }}>
            Your digital classroom companion for attendance, quizzes, and learning.
          </p>
          
          <div style={{ margin: '20px 0' }}>
            <button style={{
              backgroundColor: 'rgba(255,255,255,0.2)',
              color: 'white',
              border: '2px solid white',
              padding: '15px 30px',
              borderRadius: '8px',
              cursor: 'pointer',
              margin: '0 10px',
              fontSize: '1rem',
              fontWeight: 'bold',
              transition: 'all 0.3s'
            }}>
              Student Portal
            </button>
            <button style={{
              backgroundColor: 'white',
              color: '#667eea',
              border: '2px solid white',
              padding: '15px 30px',
              borderRadius: '8px',
              cursor: 'pointer',
              margin: '0 10px',
              fontSize: '1rem',
              fontWeight: 'bold',
              transition: 'all 0.3s'
            }}>
              Teacher Portal
            </button>
          </div>
        </div>

        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
          gap: '20px',
          marginBottom: '40px'
        }}>
          <div style={{ 
            backgroundColor: '#f8f9fa', 
            padding: '30px', 
            borderRadius: '12px',
            textAlign: 'center',
            border: '1px solid #e9ecef'
          }}>
            <div style={{ fontSize: '3rem', marginBottom: '15px' }}>📊</div>
            <h3 style={{ color: '#667eea', marginBottom: '15px' }}>Attendance Tracking</h3>
            <p>Automated face recognition attendance system with real-time monitoring and reporting.</p>
          </div>
          
          <div style={{ 
            backgroundColor: '#f8f9fa', 
            padding: '30px', 
            borderRadius: '12px',
            textAlign: 'center',
            border: '1px solid #e9ecef'
          }}>
            <div style={{ fontSize: '3rem', marginBottom: '15px' }}>🤖</div>
            <h3 style={{ color: '#764ba2', marginBottom: '15px' }}>AI Chatbot</h3>
            <p>Intelligent Q&A system powered by Google Gemini AI for instant learning support.</p>
          </div>
          
          <div style={{ 
            backgroundColor: '#f8f9fa', 
            padding: '30px', 
            borderRadius: '12px',
            textAlign: 'center',
            border: '1px solid #e9ecef'
          }}>
            <div style={{ fontSize: '3rem', marginBottom: '15px' }}>📝</div>
            <h3 style={{ color: '#667eea', marginBottom: '15px' }}>Quiz Generation</h3>
            <p>Create and manage interactive quizzes with automated grading and analytics.</p>
          </div>
        </div>

        <div style={{ 
          backgroundColor: '#f1f3f4', 
          padding: '30px', 
          borderRadius: '12px',
          textAlign: 'center'
        }}>
          <h3 style={{ marginBottom: '20px' }}>Getting Started</h3>
          <p style={{ marginBottom: '20px' }}>
            Choose your role to access the appropriate features and dashboard.
          </p>
          <div>
            <span style={{ 
              backgroundColor: '#667eea', 
              color: 'white', 
              padding: '8px 16px', 
              borderRadius: '20px',
              margin: '0 10px',
              fontSize: '0.9rem'
            }}>
              Face Recognition
            </span>
            <span style={{ 
              backgroundColor: '#764ba2', 
              color: 'white', 
              padding: '8px 16px', 
              borderRadius: '20px',
              margin: '0 10px',
              fontSize: '0.9rem'
            }}>
              AI Powered
            </span>
            <span style={{ 
              backgroundColor: '#28a745', 
              color: 'white', 
              padding: '8px 16px', 
              borderRadius: '20px',
              margin: '0 10px',
              fontSize: '0.9rem'
            }}>
              Real-time Analytics
            </span>
          </div>
        </div>
      </main>

      <footer style={{ 
        textAlign: 'center', 
        marginTop: '50px', 
        padding: '20px',
        color: '#666',
        borderTop: '1px solid #e9ecef'
      }}>
        <p>© 2024 ClassTrack - Smart Classroom Management System</p>
      </footer>
    </div>
  );
}

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);

root.render(<ClassTrackApp />);
