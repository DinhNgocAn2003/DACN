import React, { useState, useEffect } from 'react';
import { eventsAPI } from '../../services/api';
import { getCurrentUser } from '../../services/auth';

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

  useEffect(() => {
    if (event) {
      setFormData({
        event_name: event.event_name || '',
        start_time: event.start_time ? event.start_time.slice(0, 16) : '',
        end_time: event.end_time ? event.end_time.slice(0, 16) : '',
        location: event.location || '',
        time_reminder: event.time_reminder || ''
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
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const currentUser = getCurrentUser();
      const submitData = {
        ...formData,
        time_reminder: formData.time_reminder ? parseInt(formData.time_reminder) : null,
        end_time: formData.end_time || null,
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
    } catch (error) {
      setError(error.response?.data?.detail || 'Có lỗi xảy ra');
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

          <div className="form-group">
            <label>Nhắc nhở trước (phút)</label>
            <input
              type="number"
              name="time_reminder"
              value={formData.time_reminder}
              onChange={handleChange}
              min="0"
              placeholder="Ví dụ: 15"
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