import React from 'react';

const EventItem = ({ event, onEdit, onDelete }) => {
  const toVNDateKey = (d) => {
    if (!d) return null;
    const dateObj = (typeof d === 'string') ? new Date(d) : d;
    try {
      return dateObj.toLocaleDateString('en-CA', { timeZone: 'Asia/Ho_Chi_Minh' });
    } catch (e) {
      return dateObj.toISOString().slice(0,10);
    }
  };

  const formatVNDate = (d) => {
    if (!d) return '';
    const dateObj = (typeof d === 'string') ? new Date(d) : d;
    try {
      const key = dateObj.toLocaleDateString('en-CA', { timeZone: 'Asia/Ho_Chi_Minh' });
      const [y, m, day] = key.split('-');
      const time = dateObj.toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit', timeZone: 'Asia/Ho_Chi_Minh' });
      return `${day}-${m}-${y} ${time}`;
    } catch (e) {
      return dateObj.toLocaleString('vi-VN');
    }
  };

  const formatRange = (start, end) => {
    if (!start) return '';
    if (!end) return formatVNDate(start);

    const startKey = toVNDateKey(start);
    const endKey = toVNDateKey(end);
    const startObj = new Date(start);
    const endObj = new Date(end);

    // if same day, show "DD-MM-YYYY HH:MM — HH:MM"
    if (startKey && endKey && startKey === endKey) {
      try {
        const [y, m, day] = startKey.split('-');
        const startTime = startObj.toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit', timeZone: 'Asia/Ho_Chi_Minh' });
        const endTime = endObj.toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit', timeZone: 'Asia/Ho_Chi_Minh' });
        return `${day}-${m}-${y} ${startTime} — ${endTime}`;
      } catch (e) {
        return `${formatVNDate(start)} — ${formatVNDate(end)}`;
      }
    }

    // multi-day event: show full range
    return `${formatVNDate(start)} — ${formatVNDate(end)}`;
  };

  const getTimeReminderText = (minutes) => {
    if (!minutes) return 'Không nhắc nhở';
    if (minutes < 60) return `Nhắc nhở trước ${minutes} phút`;
    if (minutes < 1440) return `Nhắc nhở trước ${Math.floor(minutes/60)} giờ`;
    return `Nhắc nhở trước ${Math.floor(minutes/1440)} ngày`;
  };

  return (
    <div className="event-item">
      <div className="event-content">
        <h4>{event.event_name}</h4>

        <div className="event-details">
          <p>
            <strong>Thời gian:</strong> {formatRange(event.start_time, event.end_time)}
          </p>

          {event.location && (
            <p><strong>Địa điểm:</strong> {event.location}</p>
          )}

          <p><strong>Nhắc nhở:</strong> {getTimeReminderText(event.time_reminder)}</p>
        </div>
      </div>

      <div className="event-actions">
        <button onClick={() => onEdit(event)} className="btn-edit">Sửa</button>
        <button onClick={() => onDelete(event.id)} className="btn-delete">Xóa</button>
      </div>
    </div>
  );
};

export default EventItem;