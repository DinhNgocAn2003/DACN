import React, { useEffect, useMemo, useState } from 'react';
import { eventsAPI } from '../../services/api';

// SearchBar: tìm theo event_name hoặc location (substring, case-insensitive)
// - Khi chọn 1 result: emit CustomEvent 'event:selected' với detail { event, isMobile }

export default function SearchBar({ maxResults = 5 }) {
  const [q, setQ] = useState('');
  const [results, setResults] = useState([]);
  const [open, setOpen] = useState(false);

  // simple normalize
  const norm = (s = '') => (s || '').toString().toLowerCase();

  useEffect(() => {
    let mounted = true;
    const load = async () => {
      if (!q || q.trim().length === 0) {
        setResults([]);
        return;
      }
      try {
        const r = await eventsAPI.getEvents();
        const list = Array.isArray(r.data) ? r.data : (r.data.events || []);
        const qn = norm(q).trim();
        const filtered = (list || [])
          .filter(ev => {
            const name = norm(ev.event_name || '');
            const loc = norm(ev.location || '');
            return name.includes(qn) || loc.includes(qn);
          })
          // Sort newest-first (reverse chronological) so most recent events appear first
          .sort((a,b) => {
            const ta = a.start_time ? new Date(a.start_time).getTime() : 0;
            const tb = b.start_time ? new Date(b.start_time).getTime() : 0;
            return tb - ta;
          })
          .slice(0, maxResults);
        if (mounted) setResults(filtered);
      } catch (e) {
        console.error('Search error', e);
        setResults([]);
      }
    };

    const t = setTimeout(load, 220);
    return () => { mounted = false; clearTimeout(t); };
  }, [q, maxResults]);

  useEffect(() => {
    setOpen(results.length > 0 && q.length > 0);
  }, [results, q]);

  const isMobile = typeof window !== 'undefined' && window.innerWidth <= 768;

  const formatDateTime = (iso) => {
    if (!iso) return '';
    try {
      const d = new Date(iso);
      const timeOpts = { hour: '2-digit', minute: '2-digit', hour12: false, timeZone: 'Asia/Ho_Chi_Minh' };
      const dateOpts = { day: '2-digit', month: '2-digit', year: 'numeric', timeZone: 'Asia/Ho_Chi_Minh' };
      const timeStr = d.toLocaleTimeString('en-GB', timeOpts);
      const dateStr = d.toLocaleDateString('en-GB', dateOpts);
      return `${timeStr} ${dateStr}`; // HH:MM dd/mm/yyyy
    } catch (e) {
      return iso;
    }
  };

  function handleSelect(ev) {
    setQ('');
    setOpen(false);
    try {
      window.dispatchEvent(new CustomEvent('event:selected', { detail: { event: ev, isMobile } }));
    } catch (e) {
      // fallback: call window handler
      if (window.onEventSelected) window.onEventSelected(ev, isMobile);
    }
  }

  return (
    <div className="searchbar" style={{ position: 'relative' }}>
      <input
        className="search-input"
        placeholder="Tìm sự kiện hoặc địa điểm..."
        value={q}
        onChange={(e) => setQ(e.target.value)}
        onFocus={() => setOpen(results.length > 0)}
        onBlur={() => setTimeout(() => setOpen(false), 200)}
        aria-label="Tìm sự kiện"
      />

      {open && (
        <div className="search-results" style={{ position: 'absolute', top: '100%', left: 0, right: 0, background: '#fff', boxShadow: '0 6px 16px rgba(0,0,0,0.12)', zIndex: 50 }}>
          {results.map(ev => (
            <button key={ev.id} className="search-result-item" onMouseDown={(e)=> e.preventDefault()} onClick={() => handleSelect(ev)}>
              <div style={{ display: 'flex', flexDirection: 'column' }}>
                <div className="title">{ev.event_name}</div>
                <div className="meta">{ev.location || ''}</div>
              </div>
              <div className="meta" style={{ marginLeft: '8px' }}>{formatDateTime(ev.start_time)}</div>
            </button>
          ))}
          {results.length === 0 && <div className="no-results">Không có kết quả</div>}
        </div>
      )}
    </div>
  );
}
