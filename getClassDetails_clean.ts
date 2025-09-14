// Clean version of getClassDetails function
const getClassDetails = (): ClassDetails => {
  const currentDate = new Date();
  
  // Fixed class details for Kumar Ankit teaching DBMS
  return {
    id: 'CS301-5',
    className: 'Database Management Systems',
    subject: 'DBMS',
    teacher: 'Kumar Ankit',
    department: 'Computer Science',
    semester: 'Fall 2025',
    credits: 4,
    schedule: {
      days: ['Monday', 'Wednesday', 'Friday'],
      time: `${currentDate.toLocaleTimeString('en-US', { 
        hour: 'numeric', 
        minute: '2-digit',
        hour12: true 
      })} - ${new Date(currentDate.getTime() + 90 * 60000).toLocaleTimeString('en-US', { 
        hour: 'numeric', 
        minute: '2-digit',
        hour12: true 
      })}`,
      room: 'Tech Building - Room 201'
    },
    totalStudents: 45,
    currentSession: {
      topic: 'Advanced SQL Queries and Database Optimization',
      date: currentDate.toLocaleDateString('en-US', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      }),
      duration: '90 minutes'
    }
  };
};