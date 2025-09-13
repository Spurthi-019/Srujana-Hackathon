import React from 'react';
import { useParams } from 'react-router-dom';

const ClassroomPage: React.FC = () => {
  const { code } = useParams<{ code: string }>();
  return (
    <div className="classroom-page">
      <h2>Welcome to the Classroom</h2>
      <p><strong>Unified Code:</strong> {code}</p>
      <p>This is the resource page for the selected class and subject.</p>
      {/* Add more classroom/subject-specific resources here */}
    </div>
  );
};

export default ClassroomPage;
