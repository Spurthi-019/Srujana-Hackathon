import React from 'react';
import { useLocation, Link } from 'react-router-dom';
import './Breadcrumb.css';

interface BreadcrumbItem {
  label: string;
  path?: string;
}

const Breadcrumb: React.FC = () => {
  const location = useLocation();
  
  const getBreadcrumbs = (): BreadcrumbItem[] => {
    const pathnames = location.pathname.split('/').filter(x => x);
    const breadcrumbs: BreadcrumbItem[] = [
      { label: 'Home', path: '/' }
    ];

    pathnames.forEach((name, index) => {
      const path = `/${pathnames.slice(0, index + 1).join('/')}`;
      
      if (name === 'classroom') {
        breadcrumbs.push({ label: 'Classroom', path });
      } else if (name === 'attendance') {
        breadcrumbs.push({ label: 'Attendance' });
      } else if (name === 'quiz') {
        breadcrumbs.push({ label: 'Generate Quiz' });
      } else if (name === 'notes') {
        breadcrumbs.push({ label: 'Notes' });
      } else if (name === 'leaderboard') {
        breadcrumbs.push({ label: 'Leaderboard' });
      } else if (pathnames[index - 1] === 'classroom') {
        // This is a classroom code
        breadcrumbs.push({ label: `Class: ${decodeURIComponent(name)}`, path });
      }
    });

    return breadcrumbs;
  };

  const breadcrumbs = getBreadcrumbs();

  if (breadcrumbs.length <= 1) {
    return null; // Don't show breadcrumbs on home page
  }

  return (
    <nav className="breadcrumb-nav" aria-label="Breadcrumb">
      <ol className="breadcrumb-list">
        {breadcrumbs.map((item, index) => (
          <li key={index} className="breadcrumb-item">
            {item.path && index < breadcrumbs.length - 1 ? (
              <Link to={item.path} className="breadcrumb-link">
                {item.label}
              </Link>
            ) : (
              <span className="breadcrumb-current" aria-current="page">
                {item.label}
              </span>
            )}
            {index < breadcrumbs.length - 1 && (
              <svg 
                className="breadcrumb-separator" 
                width="16" 
                height="16" 
                viewBox="0 0 24 24" 
                fill="none"
              >
                <path 
                  d="M9 18L15 12L9 6" 
                  stroke="currentColor" 
                  strokeWidth="2" 
                  strokeLinecap="round" 
                  strokeLinejoin="round"
                />
              </svg>
            )}
          </li>
        ))}
      </ol>
    </nav>
  );
};

export default Breadcrumb;