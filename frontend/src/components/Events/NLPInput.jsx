import React, { useState, useEffect } from 'react';
import { nlpAPI, eventsAPI } from '../../services/api';
import { getCurrentUser } from '../../services/auth';

const NLPInput = ({ onEventCreated }) => {
  const [text, setText] = useState('');
  const [parsedEvent, setParsedEvent] = useState(null);
  const [formData, setFormData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleParseText = async () => {
    if (!text.trim()) return;
    
    setLoading(true);
    setError('');
    
    try {
      const response = await nlpAPI.parseText(text);
      const data = response.data || {};
      setParsedEvent(data);
      // initialize form data for editing
      setFormData({
        event_name: data.event_name || '',
        // keep datetime-local friendly format if possible
        start_time: data.start_time ? data.start_time.slice(0, 16) : '',
        end_time: data.end_time ? data.end_time.slice(0, 16) : '',
        location: data.location || '',
        time_reminder: data.time_reminder ?? ''
      });
    } catch (error) {
      setError('Không thể phân tích văn bản. Vui lòng thử lại.');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateEvent = async () => {
    try {
      const user = getCurrentUser();
      if (!user) {
        setError('Vui lòng đăng nhập để tạo sự kiện.');
        return;
      }

      // prepare payload similar to EventForm
      const submitData = {
        user_id: user.id,
        event_name: formData.event_name,
        start_time: formData.start_time,
        end_time: formData.end_time || null,
        location: formData.location || null,
        time_reminder: formData.time_reminder ? parseInt(formData.time_reminder) : null
      };

      await eventsAPI.createEvent(submitData);
      setText('');
      setParsedEvent(null);
      setFormData(null);
      setError('');
      onEventCreated();
      alert('Sự kiện đã được thêm thành công!');
    } catch (error) {
      setError(error.response?.data?.detail || 'Không thể tạo sự kiện. Vui lòng thử lại.');
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const formatDateTime = (dateTimeStr) => {
    if (!dateTimeStr) return 'Không xác định';
    return new Date(dateTimeStr).toLocaleString('vi-VN');
  };

  return (
    <div className="nlp-input">
      <h3>Thêm sự kiện bằng văn bản</h3>
      
      <div className="input-group">
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Nhập mô tả sự kiện... (VD: Họp nhóm lúc 14h chiều mai tại phòng họp 301)"
          rows="1"
        />
        <button 
          onClick={handleParseText} 
          disabled={loading || !text.trim()}
        >
          {loading ? 'Đang phân tích...' : 'Phân tích'}
        </button>
      </div>

      {error && <div className="error-message">{error}</div>}

      {parsedEvent && formData && (
        <div className="parsed-event">
          <h4>Thông tin sự kiện đã phân tích (chỉnh sửa nếu cần):</h4>
          <form className="nlp-form" onSubmit={(e) => { e.preventDefault(); handleCreateEvent(); }}>
            <div className="form-group">
              <label>Tên sự kiện *</label>
              <input type="text" name="event_name" value={formData.event_name} onChange={handleChange} required />
            </div>

            <div className="form-group">
              <label>Thời gian bắt đầu *</label>
              <input type="datetime-local" name="start_time" value={formData.start_time} onChange={handleChange} required />
            </div>

            <div className="form-group">
              <label>Thời gian kết thúc</label>
              <input type="datetime-local" name="end_time" value={formData.end_time} onChange={handleChange} />
            </div>

            <div className="form-group">
              <label>Địa điểm</label>
              <input type="text" name="location" value={formData.location} onChange={handleChange} />
            </div>

            <div className="form-group">
              <label>Nhắc nhở trước (phút)</label>
              <input type="number" name="time_reminder" value={formData.time_reminder} onChange={handleChange} min="0" />
            </div>

            <div className="action-buttons">
              <button type="submit" className="btn-primary">Thêm vào lịch</button>
              <button type="button" onClick={() => { setParsedEvent(null); setFormData(null); }} className="btn-secondary">Huỷ</button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
};

export default NLPInput;