import React, { useState, useEffect } from 'react';
import { eventsAPI } from '../../services/api';
import { useToast } from '../Common/ToastProvider';
import EventItem from './EventItem';
import EventForm from './EventForm';
import NLPInput from './NLPInput';
import Calendar from './Calendar';
import ConfirmationModal from '../Common/ConfirmationModal';
import { getCurrentUser } from '../../services/auth';

const EventList = () => {
  const [events, setEvents] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [editingEvent, setEditingEvent] = useState(null);
  const [showNLPModal, setShowNLPModal] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  // default to today so users see today's events by default
  const [selectedDate, setSelectedDate] = useState(() => new Date());

  const toast = useToast();

  const [deleteCandidate, setDeleteCandidate] = useState(null);

  const fetchEvents = async () => {
    try {
      // If user is logged in, fetch their events; otherwise fetch public events
      const user = getCurrentUser();
      const response = await eventsAPI.getEventsByUser(user.id);
      const data = response?.data ?? {};
      const list = Array.isArray(data) ? data : (data.events ?? []);
      setEvents(Array.isArray(list) ? list : []);
    } catch (error) {
      setError('Không thể tải danh sách sự kiện');
      const msg = error.response?.data?.detail || error.message || 'Không thể tải danh sách sự kiện';
      try { toast.showToast({ type: 'error', message: msg }); } catch (e) {}
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

  // Note: NLP input is shown inline on desktop and via Calendar mobile toolbar on small screens

  const handleEditEvent = (event) => {
    setEditingEvent(event);
    setShowForm(true);
  };

  const handleDeleteEvent = (id) => {
    const ev = events.find((e) => e.id === id);
    setDeleteCandidate({ id, name: ev?.event_name ?? 'sự kiện' });
  };

  const performDelete = async () => {
    if (!deleteCandidate) return;
    try {
      await eventsAPI.deleteEvent(deleteCandidate.id);
      fetchEvents();
      try { toast.showToast({ type: 'success', message: 'Xóa sự kiện thành công' }); } catch (e) {}
    } catch (error) {
      setError('Không thể xóa sự kiện');
      try { toast.showToast({ type: 'error', message: 'Không thể xóa sự kiện' }); } catch (e) {}
    } finally {
      setDeleteCandidate(null);
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
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <button onClick={handleCreateEvent} className="btn-primary">
            Thêm sự kiện mới
          </button>
          <div className="mobile-only-add">
            <button onClick={() => setShowNLPModal(true)} className="btn-secondary">Thêm bằng văn bản</button>
          </div>
        </div>
      </div>

      {error && <div className="error-message">{error}</div>}

      <div style={{ display: 'flex', gap: '1.5rem', alignItems: 'flex-start' }}>
        <div className="events-sidebar">
          <Calendar
            events={events}
            selectedDate={selectedDate}
            onSelectDate={(d) => setSelectedDate(d)}
            onEditEvent={handleEditEvent}
            onDeleteEvent={handleDeleteEvent}
            onRequestDelete={(id, name) => setDeleteCandidate({ id, name })}
          />
        </div>

        <div className="events-main">
          <div className="desktop-nlp">
            <NLPInput onEventCreated={handleEventCreated} />
          </div>
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

      {/* Mobile NLP modal (opened by the mobile-only button) */}
      {showNLPModal && (
        <div className="mobile-modal-overlay" onClick={() => setShowNLPModal(false)}>
          <div className="mobile-modal smart" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Thêm bằng văn bản</h3>
              <button className="close-btn" onClick={() => setShowNLPModal(false)}>&times;</button>
            </div>
            <NLPInput onEventCreated={() => { setShowNLPModal(false); handleEventCreated(); }} />
          </div>
        </div>
      )}

      <ConfirmationModal
        isOpen={!!deleteCandidate}
        title="Xác nhận xóa"
        message={`Bạn có chắc muốn xóa sự kiện "${deleteCandidate?.name}"?`}
        onConfirm={performDelete}
        onCancel={() => setDeleteCandidate(null)}
        confirmLabel="Xóa"
        cancelLabel="Hủy"
      />
    </div>
  );
};

export default EventList;