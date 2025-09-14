
function TestApp() {
  return (
    <div style={{ padding: '20px', textAlign: 'center' }}>
      <h1>ClassTrack Test</h1>
      <p>If you can see this, the deployment is working!</p>
      <p>Current time: {new Date().toLocaleString()}</p>
    </div>
  );
}

export default TestApp;