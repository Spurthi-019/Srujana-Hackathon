import React, { useState } from 'react';
import './SchedulePlanner.css';

interface ScheduleEvent {
  id: string;
  title: string;
  subject: string;
  startTime: string;
  endTime: string;
  date: string;
  room: string;
  type: 'lecture' | 'practical' | 'exam' | 'meeting';
  description?: string;
  students?: number;
}

interface CalendarDay {
  date: Date;
  isCurrentMonth: boolean;
  isToday: boolean;
  events: ScheduleEvent[];
}

const SchedulePlanner: React.FC = () => {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [selectedDate, setSelectedDate] = useState<Date | null>(null);
  const [events, setEvents] = useState<ScheduleEvent[]>([
    {
      id: '1',
      title: 'Data Structures Lecture',
      subject: 'Computer Science',
      startTime: '09:00',
      endTime: '10:30',
      date: '2025-09-15',
      room: 'CS-101',
      type: 'lecture',
      description: 'Introduction to Binary Trees',
      students: 45
    },
    {
      id: '2',
      title: 'Web Development Lab',
      subject: 'Computer Science',
      startTime: '11:00',
      endTime: '12:30',
      date: '2025-09-15',
      room: 'CS-Lab1',
      type: 'practical',
      description: 'React Components Workshop',
      students: 30
    },
    {
      id: '3',
      title: 'Algorithms Exam',
      subject: 'Computer Science',
      startTime: '14:00',
      endTime: '16:00',
      date: '2025-09-20',
      room: 'Exam Hall A',
      type: 'exam',
      description: 'Mid-term examination',
      students: 60
    }
  ]);
  const [showEventModal, setShowEventModal] = useState(false);
  const [editingEvent, setEditingEvent] = useState<ScheduleEvent | null>(null);
  const [viewMode, setViewMode] = useState<'month' | 'week' | 'day'>('month');

  const monthNames = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ];

  const weekDays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

  const formatDate = (date: Date): string => {
    return date.toISOString().split('T')[0];
  };

  const isSameDate = (date1: Date, date2: Date): boolean => {
    return formatDate(date1) === formatDate(date2);
  };

  const getEventsForDate = (date: string): ScheduleEvent[] => {
    return events.filter(event => event.date === date);
  };

  const generateCalendarDays = (): CalendarDay[] => {
    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();
    
    const firstDayOfMonth = new Date(year, month, 1);
    const lastDayOfMonth = new Date(year, month + 1, 0);
    const firstDayOfWeek = firstDayOfMonth.getDay();
    const daysInMonth = lastDayOfMonth.getDate();
    
    const days: CalendarDay[] = [];
    const today = new Date();
    
    // Previous month's trailing days
    const prevMonthLastDay = new Date(year, month, 0).getDate();
    for (let i = firstDayOfWeek - 1; i >= 0; i--) {
      const date = new Date(year, month - 1, prevMonthLastDay - i);
      days.push({
        date,
        isCurrentMonth: false,
        isToday: false,
        events: getEventsForDate(formatDate(date))
      });
    }
    
    // Current month days
    for (let day = 1; day <= daysInMonth; day++) {
      const date = new Date(year, month, day);
      days.push({
        date,
        isCurrentMonth: true,
        isToday: isSameDate(date, today),
        events: getEventsForDate(formatDate(date))
      });
    }
    
    // Next month's leading days
    const remainingDays = 42 - days.length; // 6 rows × 7 days = 42
    for (let day = 1; day <= remainingDays; day++) {
      const date = new Date(year, month + 1, day);
      days.push({
        date,
        isCurrentMonth: false,
        isToday: false,
        events: getEventsForDate(formatDate(date))
      });
    }
    
    return days;
  };

  const handlePrevMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() - 1, 1));
  };

  const handleNextMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 1));
  };

  const handleDateClick = (day: CalendarDay) => {
    setSelectedDate(day.date);
  };

  const handleCreateEvent = () => {
    setEditingEvent(null);
    setShowEventModal(true);
  };

  const handleEditEvent = (event: ScheduleEvent) => {
    setEditingEvent(event);
    setShowEventModal(true);
  };

  const handleSaveEvent = (eventData: Partial<ScheduleEvent>) => {
    if (editingEvent) {
      // Update existing event
      setEvents(events.map(event => 
        event.id === editingEvent.id 
          ? { ...event, ...eventData }
          : event
      ));
    } else {
      // Create new event
      const newEvent: ScheduleEvent = {
        id: Date.now().toString(),
        title: eventData.title || '',
        subject: eventData.subject || '',
        startTime: eventData.startTime || '',
        endTime: eventData.endTime || '',
        date: eventData.date || formatDate(selectedDate || new Date()),
        room: eventData.room || '',
        type: eventData.type || 'lecture',
        description: eventData.description || '',
        students: eventData.students || 0
      };
      setEvents([...events, newEvent]);
    }
    setShowEventModal(false);
    setEditingEvent(null);
  };

  const handleDeleteEvent = (eventId: string) => {
    setEvents(events.filter(event => event.id !== eventId));
  };

  const getEventTypeColor = (type: string): string => {
    switch (type) {
      case 'lecture': return 'var(--accent-primary)';
      case 'practical': return 'var(--accent-secondary)';
      case 'exam': return 'var(--accent-tertiary)';
      case 'meeting': return '#fbbf24';
      default: return 'var(--accent-primary)';
    }
  };

  const renderCalendarView = () => {
    const calendarDays = generateCalendarDays();
    
    return (
      <div className="calendar-view">
        <div className="calendar-header">
          <button className="nav-btn" onClick={handlePrevMonth}>
            ‹
          </button>
          <h3>{monthNames[currentDate.getMonth()]} {currentDate.getFullYear()}</h3>
          <button className="nav-btn" onClick={handleNextMonth}>
            ›
          </button>
        </div>
        
        <div className="calendar-grid">
          <div className="calendar-weekdays">
            {weekDays.map(day => (
              <div key={day} className="weekday">{day}</div>
            ))}
          </div>
          
          <div className="calendar-days">
            {calendarDays.map((day, index) => (
              <div
                key={index}
                className={`calendar-day ${!day.isCurrentMonth ? 'other-month' : ''} 
                          ${day.isToday ? 'today' : ''} 
                          ${selectedDate && isSameDate(day.date, selectedDate) ? 'selected' : ''}
                          ${day.events.length > 0 ? 'has-events' : ''}`}
                onClick={() => handleDateClick(day)}
              >
                <span className="day-number">{day.date.getDate()}</span>
                {day.events.length > 0 && (
                  <div className="event-indicators">
                    {day.events.slice(0, 3).map((event, idx) => (
                      <div
                        key={idx}
                        className="event-dot"
                        style={{ backgroundColor: getEventTypeColor(event.type) }}
                        title={`${event.title} - ${event.startTime}`}
                      ></div>
                    ))}
                    {day.events.length > 3 && (
                      <span className="more-events">+{day.events.length - 3}</span>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  };

  const renderEventList = () => {
    const selectedEvents = selectedDate 
      ? getEventsForDate(formatDate(selectedDate))
      : events.filter(event => 
          new Date(event.date).getMonth() === currentDate.getMonth() &&
          new Date(event.date).getFullYear() === currentDate.getFullYear()
        );

    return (
      <div className="event-list">
        <div className="event-list-header">
          <h4>
            {selectedDate 
              ? `Events for ${selectedDate.toLocaleDateString()}`
              : `Events for ${monthNames[currentDate.getMonth()]} ${currentDate.getFullYear()}`
            }
          </h4>
          <button className="create-event-btn" onClick={handleCreateEvent}>
            + Add Event
          </button>
        </div>
        
        {selectedEvents.length === 0 ? (
          <div className="no-events">
            <p>No events scheduled for this period.</p>
          </div>
        ) : (
          <div className="events">
            {selectedEvents
              .sort((a, b) => a.startTime.localeCompare(b.startTime))
              .map(event => (
                <div
                  key={event.id}
                  className="event-item"
                  style={{ borderLeftColor: getEventTypeColor(event.type) }}
                >
                  <div className="event-time">
                    <span className="time">{event.startTime} - {event.endTime}</span>
                    <span className="duration">
                      {Math.abs(
                        new Date(`2000-01-01T${event.endTime}`).getTime() - 
                        new Date(`2000-01-01T${event.startTime}`).getTime()
                      ) / (1000 * 60)} mins
                    </span>
                  </div>
                  
                  <div className="event-content">
                    <h5>{event.title}</h5>
                    <p className="event-details">
                      <span className="subject">{event.subject}</span>
                      <span className="room">📍 {event.room}</span>
                      {event.students && <span className="students">👥 {event.students} students</span>}
                    </p>
                    {event.description && (
                      <p className="event-description">{event.description}</p>
                    )}
                  </div>
                  
                  <div className="event-actions">
                    <button 
                      className="edit-btn"
                      onClick={() => handleEditEvent(event)}
                    >
                      ✏️
                    </button>
                    <button 
                      className="delete-btn"
                      onClick={() => handleDeleteEvent(event.id)}
                    >
                      🗑️
                    </button>
                  </div>
                </div>
              ))}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="schedule-planner-container">
      <div className="planner-header">
        <h2>📅 Schedule Planner</h2>
        <p>Create and manage your teaching schedule with our enhanced calendar planner</p>
        
        <div className="view-controls">
          <div className="view-mode-selector">
            {['month', 'week', 'day'].map(mode => (
              <button
                key={mode}
                className={`view-mode-btn ${viewMode === mode ? 'active' : ''}`}
                onClick={() => setViewMode(mode as any)}
              >
                {mode.charAt(0).toUpperCase() + mode.slice(1)}
              </button>
            ))}
          </div>
          
          <button className="quick-add-btn" onClick={handleCreateEvent}>
            + Quick Add
          </button>
        </div>
      </div>

      <div className="planner-content">
        <div className="calendar-section">
          {renderCalendarView()}
        </div>
        
        <div className="events-section">
          {renderEventList()}
        </div>
      </div>

      {/* Event Modal would go here - simplified for now */}
      {showEventModal && (
        <div className="event-modal-overlay" onClick={() => setShowEventModal(false)}>
          <div className="event-modal" onClick={e => e.stopPropagation()}>
            <h3>{editingEvent ? 'Edit Event' : 'Create New Event'}</h3>
            <p>Event creation form would be implemented here</p>
            <div className="modal-actions">
              <button onClick={() => setShowEventModal(false)}>Cancel</button>
              <button onClick={() => handleSaveEvent({})}>Save</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SchedulePlanner;