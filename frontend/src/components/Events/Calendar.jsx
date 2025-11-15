import React, { useState, useMemo } from 'react';

// Simple calendar month view that shows event counts per day.
const Calendar = ({ events = [], selectedDate, onSelectDate, onEditEvent, onDeleteEvent, onCreateEvent }) => {
  // Use Vietnam timezone key helper early so we can initialize calendar month to VN today
  const dateKeyVN = (d) => {
    if (!d) return null;
    const dateObj = (typeof d === 'string') ? new Date(d) : d;
    try {
      return dateObj.toLocaleDateString('en-CA', { timeZone: 'Asia/Ho_Chi_Minh' });
    } catch (e) {
      return dateObj.toISOString().slice(0,10);
    }
  };

  const [current, setCurrent] = useState(() => {
    // Initialize to the VN month for "today"
    const nowKey = dateKeyVN(new Date());
    if (nowKey) {
      const [y, m] = nowKey.split('-');
      return new Date(parseInt(y,10), parseInt(m,10) - 1, 1);
    }
    const d = selectedDate ? new Date(selectedDate) : new Date();
    return new Date(d.getFullYear(), d.getMonth(), 1);
  });
  const [modalDate, setModalDate] = useState(null);


  // Helper to format date keys and display dates in VN timezone
  const formatDateKeyVN = (d) => {
    if (!d) return null;
    const dateObj = (typeof d === 'string') ? new Date(d) : d;
    try {
      return dateObj.toLocaleDateString('en-CA', { timeZone: 'Asia/Ho_Chi_Minh' });
    } catch (e) {
      return dateObj.toISOString().slice(0,10);
    }
  };

  const formatDateVN = (d) => {
    const key = formatDateKeyVN(d);
    if (!key) return '';
    const [y, m, day] = key.split('-');
    return `${day}-${m}-${y}`;
  };

  // Build a map of dateKey -> array of events covering that date (handles multi-day events)
  const eventsByDate = useMemo(() => {
    const map = {};

    const addToKey = (key, ev, meta = {}) => {
      if (!key) return;
      if (!map[key]) map[key] = [];
      map[key].push({ ...ev, ...meta });
    };

    const parseKeyToDate = (key) => {
      // key is YYYY-MM-DD
      const [y, m, d] = key.split('-').map(Number);
      return new Date(y, m - 1, d);
    };

    events.forEach(ev => {
      if (!ev?.start_time) return;
      const startKey = formatDateKeyVN(ev.start_time);
      const endKey = ev.end_time ? formatDateKeyVN(ev.end_time) : startKey;
      if (!startKey) return;

      // iterate from startKey to endKey inclusive
      let cur = parseKeyToDate(startKey);
      const end = parseKeyToDate(endKey);
      while (cur <= end) {
        const k = formatDateKeyVN(cur);
        const isStart = k === startKey;
        const isEnd = k === endKey;
        addToKey(k, ev, { isStart, isEnd });
        cur = new Date(cur.getFullYear(), cur.getMonth(), cur.getDate() + 1);
      }
    });

    // ensure arrays are stable order (by start_time)
    Object.keys(map).forEach(k => {
      map[k].sort((a, b) => new Date(a.start_time) - new Date(b.start_time));
    });

    return map;
  }, [events]);

  const startDay = current.getDay(); // 0..6 (Sun..Sat)
  const daysInMonth = new Date(current.getFullYear(), current.getMonth()+1, 0).getDate();

  const prev = () => setCurrent(c => new Date(c.getFullYear(), c.getMonth() - 1, 1));
  const next = () => setCurrent(c => new Date(c.getFullYear(), c.getMonth() + 1, 1));

  const weeks = [];
  let day = 1 - startDay; // start from negative/zero to fill leading blanks
  while (day <= daysInMonth) {
    const week = [];
    for (let i = 0; i < 7; i++, day++) {
      if (day < 1 || day > daysInMonth) {
        week.push(null);
      } else {
        week.push(new Date(current.getFullYear(), current.getMonth(), day));
      }
    }
    weeks.push(week);
  }

  const isSameDay = (a, b) => a && b && a.getFullYear() === b.getFullYear() && a.getMonth() === b.getMonth() && a.getDate() === b.getDate();

  return (
    <div className="calendar">
      <div className="calendar-header">
        <button onClick={prev} className="btn-secondary">‹</button>
        <div className="calendar-title">{current.toLocaleString(undefined, { month: 'long', year: 'numeric' })}</div>
        <button onClick={next} className="btn-secondary">›</button>
      </div>

      <div className="calendar-grid">
        <div className="calendar-weekday">Sun</div>
        <div className="calendar-weekday">Mon</div>
        <div className="calendar-weekday">Tue</div>
        <div className="calendar-weekday">Wed</div>
        <div className="calendar-weekday">Thu</div>
        <div className="calendar-weekday">Fri</div>
        <div className="calendar-weekday">Sat</div>

          {weeks.map((week, wi) => (
            week.map((d, di) => {
              const key = d ? formatDateKeyVN(d) : `empty-${wi}-${di}`;
              const dayEventsFull = d ? (eventsByDate[key] || []) : [];
              // filter out events that are fully in the past for calendar grid display
              const now = new Date();
              const isEventPast = (ev) => {
                const tStr = ev.end_time || ev.start_time;
                if (!tStr) return false;
                const t = new Date(tStr);
                if (isNaN(t.getTime())) return false;
                return t < now;
              };
              const dayEvents = dayEventsFull.filter(ev => !isEventPast(ev));
              const count = dayEvents.length;
              const selected = d && selectedDate ? isSameDay(d, new Date(selectedDate)) : false;
              const todayKey = formatDateKeyVN(new Date());
              const isToday = d ? key === todayKey : false;
              const hasEvent = count > 0;
              const classes = [
                'calendar-day',
                d ? '' : 'empty',
                selected ? 'selected' : '',
                isToday ? 'today' : '',
                hasEvent ? 'has-event' : ''
              ].filter(Boolean).join(' ');

              const handleDayClick = (dayDate) => {
                if (!dayDate) return;
                // notify parent (desktop) to set selectedDate
                if (onSelectDate) {
                  try { onSelectDate(dayDate); } catch (e) {}
                }
                // on small screens, open the modal listing so user can see events
                try {
                  if (typeof window !== 'undefined' && window.innerWidth <= 992) {
                    setModalDate(dayDate);
                    return;
                  }
                } catch (e) {}
                // otherwise, if no parent handler provided, open modal as fallback
                if (!onSelectDate) setModalDate(dayDate);
              };

              return (
                <div key={key} className={classes} onClick={() => handleDayClick(d)}>
                  {d && (
                    <>
                      <div className="day-number">{d.getDate()}</div>
                      {count > 0 && <div className="event-count">{count}</div>}
                      {/* event bars (show up to 3) */}
                      {dayEvents.length > 0 && (
                        <div className="event-bars">
                          {dayEvents.slice(0, 3).map((ev, idx) => (
                            <div key={ev.id + '-' + idx} className={`event-bar ${ev.isStart ? 'start' : ''} ${ev.isEnd ? 'end' : ''}`} title={ev.event_name} />
                          ))}
                          {dayEvents.length > 3 && <div className="more-badge">+{dayEvents.length - 3}</div>}
                        </div>
                      )}
                      {isToday && <div className="today-dot" aria-hidden="true" />}
                    </>
                  )}
                </div>
              )
            })
          ))}
      </div>

      {/* Mobile toolbar removed; mobile actions are handled by parent (EventList) */}

        {/* Modal showing events for clicked date when modalDate is set */}
        {modalDate && (
          <div className="modal-overlay" onClick={() => setModalDate(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
              <div className="modal-header">
              <h3>Sự kiện cho {formatDateVN(modalDate)}</h3>
                <button className="close-btn" onClick={() => setModalDate(null)}>&times;</button>
              </div>
              <div style={{ maxHeight: '60vh', overflowY: 'auto' }}>
                {(() => {
                const key = formatDateKeyVN(modalDate);
                let dayEvents = eventsByDate[key] || [];
                  if (dayEvents.length === 0) return <p>Không có sự kiện.</p>;
                  dayEvents = [...dayEvents].sort((a,b) => new Date(a.start_time) - new Date(b.start_time));
                  return dayEvents.map(ev => (
                    <div key={ev.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0.5rem 0', borderBottom: '1px solid #eee' }}>
                      <div>
                        <div style={{ fontWeight: 600 }}>{ev.event_name}</div>
                        <div style={{ fontSize: '0.9rem', color: '#666' }}>{(() => {
                          // show time range or single time, respecting VN timezone
                          const s = ev.start_time;
                          const e = ev.end_time;
                          const toKey = (d) => {
                            if (!d) return null;
                            const o = (typeof d === 'string') ? new Date(d) : d;
                            try { return o.toLocaleDateString('en-CA', { timeZone: 'Asia/Ho_Chi_Minh' }); } catch { return o.toISOString().slice(0,10); }
                          };
                          const formatTime = (d) => {
                            const o = (typeof d === 'string') ? new Date(d) : d;
                            return o.toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit', timeZone: 'Asia/Ho_Chi_Minh' });
                          };
                          if (!s) return ev.location || 'Không rõ';
                          if (!e) return `${formatTime(s)} - ${ev.location || 'Không rõ'}`;
                          const sk = toKey(s);
                          const ek = toKey(e);
                          if (sk && ek && sk === ek) {
                            return `${sk.split('-').reverse().join('-')} ${formatTime(s)} — ${formatTime(e)} - ${ev.location || 'Không rõ'}`;
                          }
                          // multi-day
                          const formatDate = (d) => { const o = (typeof d === 'string') ? new Date(d) : d; try { const k = o.toLocaleDateString('en-CA', { timeZone: 'Asia/Ho_Chi_Minh' }); const [y,m,dd] = k.split('-'); return `${dd}-${m}-${y} ${formatTime(o)}` } catch { return o.toLocaleString('vi-VN'); } };
                          return `${formatDate(s)} — ${formatDate(e)} - ${ev.location || 'Không rõ'}`;
                        })()}</div>
                      </div>
                      <div style={{ display: 'flex', gap: '0.5rem' }}>
                        {onEditEvent && <button className="btn-edit" onClick={() => { setModalDate(null); onEditEvent(ev); }}>Sửa</button>}
                        {onDeleteEvent && <button className="btn-delete" onClick={async () => { if (confirm('Xác nhận xóa?')) { await onDeleteEvent(ev.id); setModalDate(null); } }}>Xóa</button>}
                      </div>
                    </div>
                  ));
                })()}
              </div>
            </div>
          </div>
        )}

      {/* Mobile add modals were moved to EventList (parent) so calendar stays focused */}
    </div>
  );
};

export default Calendar;

