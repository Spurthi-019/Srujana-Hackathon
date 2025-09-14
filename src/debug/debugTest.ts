// Debug test file to verify breakpoint functionality
export const debugTest = () => {
  console.log('Debug test function called');
  
  // Test breakpoint here
  const testData = {
    message: 'Full stack debugging is working!',
    timestamp: new Date().toISOString(),
    frontend: 'React with TypeScript',
    backend: 'Flask with Python',
    authentication: 'Clerk',
    database: 'Firebase (Mock Mode)'
  };
  
  console.log('Debug test data:', testData);
  return testData;
};

export default debugTest;