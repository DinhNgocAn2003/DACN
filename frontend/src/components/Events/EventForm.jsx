import React, { useState, useEffect } from 'react';
import { eventsAPI } from '../../services/api';
import { getCurrentUser } from '../../services/auth';
import { useToast } from '../Common/ToastProvider';

const EventForm = ({ event, initialDate, onClose, onSuccess }) => {
  const [formData, setFormData] = useState({
    event_name: '',
    start_time: '',
    end_time: '',
    location: '',
    time_reminder: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { showToast } = useToast();

  useEffect(() => {
    if (event) {
      setFormData({
        event_name: event.event_name || '',
        start_time: event.start_time ? event.start_time.slice(0, 16) : '',
        end_time: event.end_time ? event.end_time.slice(0, 16) : '',
        location: event.location || '',
        time_reminder: event.time_reminder ?? ''
      });
    } else if (initialDate) {
      // Prefill start_time from calendar selected date. Default to 09:00 on that date.
      const d = (typeof initialDate === 'string') ? new Date(initialDate) : initialDate;
      const yyyy = d.getFullYear();
      const mm = String(d.getMonth() + 1).padStart(2, '0');
      const dd = String(d.getDate()).padStart(2, '0');
      const hh = '09';
      const mins = '00';
      setFormData(prev => ({
        ...prev,
        start_time: `${yyyy}-${mm}-${dd}T${hh}:${mins}`,
        end_time: ''
      }));
    }
  }, [event, initialDate]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    // if start_time is cleared, also clear dependent fields
    if (name === 'start_time' && !value) {
      setFormData(prev => ({ ...prev, start_time: '', end_time: '', time_reminder: '' }));
      return;
    }
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    
    try {
      const currentUser = getCurrentUser();
      const formatForBackend = (s) => {
        if (!s) return null;
        if (s.includes('T')) {
          const v = s.replace('T', ' ');
          return v.length === 16 ? `${v}:00` : v;
        }
        return s;
      };

      const submitData = {
        ...formData,
        time_reminder: formData.time_reminder ? parseInt(formData.time_reminder) : null,
        start_time: formatForBackend(formData.start_time),
        end_time: formatForBackend(formData.end_time),
        // ensure user_id is provided (use existing event.user_id when editing)
        user_id: event ? event.user_id : (currentUser ? currentUser.id : null)
      };

      if (!submitData.user_id) {
        throw new Error('Người dùng chưa đăng nhập. Vui lòng đăng nhập để tạo sự kiện.');
      }

      if (event) {
        await eventsAPI.updateEvent(event.id, submitData);
      } else {
        await eventsAPI.createEvent(submitData);
      }
      onSuccess();
      showToast({ type: 'success', message: event ? 'Cập nhật sự kiện thành công' : 'Thêm sự kiện thành công' });
    } catch (error) {
      const msg = error.response?.data?.detail || error.message || 'Có lỗi xảy ra';
      setError(msg);
      // show toast for failure
      try { showToast({ type: 'error', message: msg }); } catch (e) { /* ignore */ }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <div className="modal-header">
          <h3>{event ? 'Chỉnh sửa sự kiện' : 'Thêm sự kiện mới'}</h3>
          <button onClick={onClose} className="close-btn">&times;</button>
        </div>

        {error && <div className="error-message">{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Tên sự kiện *</label>
            <input
              type="text"
              name="event_name"
              value={formData.event_name}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label>Thời gian bắt đầu *</label>
            <input
              type="datetime-local"
              name="start_time"
              value={formData.start_time}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label>Thời gian kết thúc</label>
            <input
              type="datetime-local"
              name="end_time"
              value={formData.end_time}
              onChange={handleChange}
              disabled={!formData.start_time}
            />
          </div>

          <div className="form-group">
            <label>Nhắc nhở trước (phút)</label>
            <input
              type="number"
              name="time_reminder"
              value={formData.time_reminder}
              onChange={handleChange}
              min="0"
              placeholder="Ví dụ: 15"
              disabled={!formData.start_time}
            />
          </div>

          <div className="form-group">
            <label>Địa điểm</label>
            <input
              type="text"
              name="location"
              value={formData.location}
              onChange={handleChange}
            />
          </div>

          <div className="form-actions">
            <button type="button" onClick={onClose} className="btn-secondary">
              Huỷ
            </button>
            <button type="submit" disabled={loading} className="btn-primary">
              {loading ? 'Đang lưu...' : (event ? 'Cập nhật' : 'Thêm sự kiện')}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default EventForm;