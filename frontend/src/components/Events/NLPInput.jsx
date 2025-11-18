import React, { useState, useEffect } from 'react';
import { nlpAPI, eventsAPI } from '../../services/api';
import { getCurrentUser } from '../../services/auth';
import { useToast } from '../Common/ToastProvider';

const NLPInput = ({ onEventCreated }) => {
  const [text, setText] = useState('');
  const [parsedEvent, setParsedEvent] = useState(null);
  const [formData, setFormData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { showToast } = useToast();

  const handleParseText = async () => {
    if (!text.trim()) return;

    setParsedEvent(null);
    setFormData(null);
    setError('');


    const timePattern = /(\d{1,2}[:h]\d{0,2}|\d{1,2}\s*(giờ|h|phút)|\blúc\b|\bvào\b|\b(sáng|chiều|tối|đêm|trưa)\b|\b(hôm nay|ngày mai|mai|tuần|tháng|thứ)\b)/i;
    if (!timePattern.test(text)) {
      const msg = 'Phân tích không thành công, vui lòng nhập đầy đủ thông tin hơn';
      setError(msg);
      try { showToast({ type: 'error', message: msg }); } catch (e) {}
      return;
    }

    setLoading(true);
    
    try {
      const response = await nlpAPI.parseText(text);
      const data = response.data || {};

      if (!data.start_time) {
        const msg = 'Phân tích không thành công, vui lòng nhập đầy đủ thông tin hơn (thời gian bắt đầu)';
        setError(msg);
        try { showToast({ type: 'error', message: msg }); } catch (e) {}
        setParsedEvent(null);
        setFormData(null);
        return;
      }


      setParsedEvent(data);
      try { showToast({ type: 'success', message: 'Phân tích văn bản thành công' }); } catch (e) {}

      const hasStart = !!data.start_time;

      const toDateTimeLocal = (s) => {
        if (!s) return '';
        // backend returns 'YYYY-MM-DD HH:MM:SS' — convert to 'YYYY-MM-DDTHH:MM' for datetime-local
        const normalized = s.replace(' ', 'T');
        return normalized.slice(0, 16);
      };

      setFormData({
        event_name: data.event_name || '',
        // convert backend datetime to datetime-local input value
        start_time: hasStart ? toDateTimeLocal(data.start_time) : '',
        end_time: hasStart && data.end_time ? toDateTimeLocal(data.end_time) : '',
        location: data.location || '',
        time_reminder: hasStart ? (data.time_reminder ?? '') : ''
      });
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

      const formatForBackend = (s) => {
        if (!s) return null;
        // if datetime-local 'YYYY-MM-DDTHH:MM' -> 'YYYY-MM-DD HH:MM:00'
        if (s.includes('T')) {
          const v = s.replace('T', ' ');
          return v.length === 16 ? `${v}:00` : v;
        }
        return s;
      };

      const hasStart = !!formData?.start_time;
      const submitData = {
        user_id: user.id,
        event_name: formData.event_name,
        start_time: formatForBackend(formData.start_time),
        end_time: hasStart ? formatForBackend(formData.end_time) : null,
        location: formData.location || null,
        time_reminder: hasStart && formData.time_reminder ? parseInt(formData.time_reminder) : null
      };

      await eventsAPI.createEvent(submitData);
      setText('');
      setParsedEvent(null);
      setFormData(null);
      setError('');
      onEventCreated();
      try { showToast({ type: 'success', message: 'Sự kiện đã được thêm thành công' }); } catch (e) {}
    } catch (error) {
      const msg = error.response?.data?.detail || 'Không thể tạo sự kiện. Vui lòng thử lại.';
      setError(msg);
      try { showToast({ type: 'error', message: msg }); } catch (e) {}
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => {
      if (!prev) return prev;
      // if user clears start_time, also clear dependent fields
      if (name === 'start_time' && !value) {
        return { ...prev, start_time: '', end_time: '', time_reminder: '' };
      }
      return { ...prev, [name]: value };
    });
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
              <input type="datetime-local" name="end_time" value={formData.end_time} onChange={handleChange} disabled={!formData.start_time} />
            </div>

            <div className="form-group">
              <label>Địa điểm</label>
              <input type="text" name="location" value={formData.location} onChange={handleChange} />
            </div>

            <div className="form-group">
              <label>Nhắc nhở trước (phút)</label>
              <input type="number" name="time_reminder" value={formData.time_reminder} onChange={handleChange} min="0" disabled={!formData.start_time} />
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