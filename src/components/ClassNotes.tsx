import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import '../mouse-bg-effect.css';
import { apiService } from '../services/api';
import './ClassNotes.css';

interface Material {
  url: string;
  title: string;
  type: string;
  teacher_name?: string;
}

const ClassNotes: React.FC = () => {
  useEffect(() => {
    const bg = document.querySelector('.mouse-bg-effect') as HTMLElement;
    const move = (e: MouseEvent) => {
      if (bg) {
        bg.style.setProperty('--x', `${e.clientX}px`);
        bg.style.setProperty('--y', `${e.clientY}px`);
      }
    };
    window.addEventListener('mousemove', move);
    return () => window.removeEventListener('mousemove', move);
  }, []);
  const { classroomId } = useParams<{ classroomId: string }>();
  const [materials, setMaterials] = useState<Material[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchNotes = async () => {
      try {
  const res: any = await apiService.getClassDetails(classroomId!);
  // Assume backend returns recent_materials or notes with teacher info
  setMaterials(res.recent_materials || res.notes || []);
      } catch (err: any) {
        setError('Failed to load notes');
      } finally {
        setLoading(false);
      }
    };
    fetchNotes();
  }, [classroomId]);

  if (loading) return <div>Loading notes...</div>;
  if (error) return <div>{error}</div>;

  return (
    <>
      <div className="mouse-bg-effect"></div>
      <div className="class-notes-page">
        <h2>Class Notes</h2>
        {materials.length === 0 && <div>No notes uploaded yet.</div>}
        {materials.map((mat, idx) => (
          <div key={idx} className="note-card">
            <h4>{mat.title}</h4>
            {mat.teacher_name && <div>Uploaded by: {mat.teacher_name}</div>}
            {mat.type === 'pdf' && (
              <iframe src={mat.url} title={mat.title} width="100%" height="500px" />
            )}
            {/* Add support for other file types if needed */}
          </div>
        ))}
      </div>
    </>
  );
};

export default ClassNotes;
