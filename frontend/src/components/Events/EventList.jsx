import React, { useState, useEffect } from 'react';
import { eventsAPI } from '../../services/api';
import EventItem from './EventItem';
import EventForm from './EventForm';
import NLPInput from './NLPInput';
import Calendar from './Calendar';

const EventList = () => {
  const [events, setEvents] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [editingEvent, setEditingEvent] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  // default to today so users see today's events by default
  const [selectedDate, setSelectedDate] = useState(() => new Date());

  const fetchEvents = async () => {
    try {
      const response = await eventsAPI.getEvents();
      // console.log('Fetched events:', response.data);
      // Backend returns { events: [...], count: n }.
      // Accept either a plain array or the wrapped object for compatibility.
      const data = response.data;
      const list = Array.isArray(data) ? data : (data?.events ?? []);
      setEvents(list);
    } catch (error) {
      setError('Không thể tải danh sách sự kiện');
      console.log(error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEvents();
  }, []);

  const handleCreateEvent = () => {
    setEditingEvent(null);
    setShowForm(true);
  };

  const handleEditEvent = (event) => {
    setEditingEvent(event);
    setShowForm(true);
  };

  const handleDeleteEvent = async (id) => {
    if (window.confirm('Bạn có chắc muốn xóa sự kiện này?')) {
      try {
        await eventsAPI.deleteEvent(id);
        fetchEvents();
      } catch (error) {
        setError('Không thể xóa sự kiện');
      }
    }
  };

  const handleFormClose = () => {
    setShowForm(false);
    setEditingEvent(null);
  };

  const handleEventCreated = () => {
    fetchEvents();
    setShowForm(false);
  };

  if (loading) return <div className="loading">Đang tải...</div>;

  return (
    <div className="event-list">
      <div className="event-header">
        <h2>Lịch trình của tôi</h2>
        <button onClick={handleCreateEvent} className="btn-primary">
          Thêm sự kiện mới
        </button>
      </div>

      {error && <div className="error-message">{error}</div>}

      <div style={{ display: 'flex', gap: '1.5rem', alignItems: 'flex-start' }}>
        <div className="events-sidebar">
          <Calendar events={events} selectedDate={selectedDate} onSelectDate={(d) => setSelectedDate(d)} onEditEvent={handleEditEvent} onDeleteEvent={handleDeleteEvent} />
        </div>

        <div className="events-main">
          <NLPInput onEventCreated={handleEventCreated} />

          <div style={{ marginBottom: '1rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h3>{selectedDate ? `Sự kiện cho ${(() => { const k = (typeof selectedDate === 'string') ? (new Date(selectedDate)).toLocaleDateString('en-CA', { timeZone: 'Asia/Ho_Chi_Minh' }) : (new Date(selectedDate)).toLocaleDateString('en-CA', { timeZone: 'Asia/Ho_Chi_Minh' }); const [y,m,day] = k.split('-'); return `${day}-${m}-${y}` })()}` : 'Chọn một ngày trên lịch để xem sự kiện'}</h3>
            {selectedDate && <button className="btn-secondary" onClick={() => setSelectedDate(null)}>Xóa bộ lọc</button>}
          </div>

          <div className="events-container">
            {selectedDate ? (() => {
              const dateKeyVN = (d) => {
                if (!d) return null;
                const dateObj = (typeof d === 'string') ? new Date(d) : d;
                try {
                  return dateObj.toLocaleDateString('en-CA', { timeZone: 'Asia/Ho_Chi_Minh' });
                } catch (e) {
                  return dateObj.toISOString().slice(0,10);
                }
              };

              // include events that cover the selected date (multi-day events)
              const selKey = dateKeyVN(selectedDate);
              let listToShow = events.filter(ev => {
                if (!ev?.start_time) return false;
                const startKey = dateKeyVN(ev.start_time);
                const endKey = ev.end_time ? dateKeyVN(ev.end_time) : startKey;
                if (!startKey) return false;
                // keys are YYYY-MM-DD so lexicographic comparison works
                return startKey <= selKey && selKey <= endKey;
              });

              // sort by start_time ascending
              listToShow = listToShow.sort((a,b) => new Date(a.start_time) - new Date(b.start_time));

              if (listToShow.length === 0) {
                return (
                  <div className="empty-state">
                    <p>Không có sự kiện cho ngày đã chọn.</p>
                  </div>
                )
              }

              return listToShow.map(event => (
                <EventItem
                  key={event.id}
                  event={event}
                  onEdit={handleEditEvent}
                  onDelete={handleDeleteEvent}
                />
              ));
            })() : (
              <div className="empty-state">
                <p>Vui lòng chọn một ngày trên lịch để xem các sự kiện.</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {showForm && (
        <EventForm
          event={editingEvent}
          initialDate={selectedDate}
          onClose={handleFormClose}
          onSuccess={handleEventCreated}
        />
      )}
    </div>
  );
};

export default EventList;