import React from 'react';
import ReactDOM from 'react-dom/client';

function TestApp() {
  return React.createElement('div', { 
    style: { padding: '20px', textAlign: 'center', fontFamily: 'Arial' }
  }, [
    React.createElement('h1', { key: 'title' }, 'ClassTrack Test'),
    React.createElement('p', { key: 'msg' }, 'If you can see this, the deployment is working!'),
    React.createElement('p', { key: 'time' }, `Current time: ${new Date().toLocaleString()}`)
  ]);
}

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);

root.render(React.createElement(TestApp));