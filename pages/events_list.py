"""
Trang danh sách sự kiện
"""
import streamlit as st
from datetime import datetime, timedelta
from utils.database import get_events, delete_event

def events_list_page():
    """Trang danh sách sự kiện"""
    st.markdown("""
        <div style='background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%); 
                    padding: 1.5rem; border-radius: 20px; margin-bottom: 1.5rem; text-align: center;'>
            <h2 style='color: #2d3748; margin: 0; font-size: 2rem;'>📋 Danh Sách Sự Kiện</h2>
            <p style='color: #718096; margin: 0.5rem 0 0 0;'>Quản lý tất cả sự kiện của bạn</p>
        </div>
    """, unsafe_allow_html=True)
    
    events = get_events(st.session_state.user_id)
    
    if events:
        # Filter options
        col1, col2, col3 = st.columns(3)
        with col1:
            filter_option = st.selectbox("Lọc theo:", ["Tất cả", "Hôm nay", "Tuần này", "Tháng này"])
        
        now = datetime.now()
        filtered_events = []
        
        for event in events:
            event_start = datetime.strptime(event['start_time'], '%Y-%m-%d %H:%M:%S')
            
            if filter_option == "Tất cả":
                filtered_events.append(event)
            elif filter_option == "Hôm nay":
                if event_start.date() == now.date():
                    filtered_events.append(event)
            elif filter_option == "Tuần này":
                week_start = now - timedelta(days=now.weekday())
                week_end = week_start + timedelta(days=7)
                if week_start.date() <= event_start.date() < week_end.date():
                    filtered_events.append(event)
            elif filter_option == "Tháng này":
                if event_start.month == now.month and event_start.year == now.year:
                    filtered_events.append(event)
        
        if filtered_events:
            st.markdown(f"""
                <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                            color: white; padding: 1rem; border-radius: 10px; margin-bottom: 1rem; text-align: center;'>
                    <h3 style='margin: 0;'>🎯 Tìm thấy {len(filtered_events)} sự kiện</h3>
                </div>
            """, unsafe_allow_html=True)
            
            for event in filtered_events:
                event_start = datetime.strptime(event['start_time'], '%Y-%m-%d %H:%M:%S')
                event_end = datetime.strptime(event['end_time'], '%Y-%m-%d %H:%M:%S')
                
                # Kiểm tra sự kiện đã qua chưa
                is_past = event_end < now
                
                with st.container():
                    col1, col2 = st.columns([5, 1])
                    
                    with col1:
                        status = "⏳ Đã qua" if is_past else "✅ Sắp tới"
                        st.markdown(f"""
                        <div class='event-card'>
                            <h3>{event['event_name']} <span style='color: gray; font-size: 0.8rem;'>({status})</span></h3>
                            <p>🕐 <strong>Bắt đầu:</strong> {event_start.strftime('%d/%m/%Y %H:%M')}</p>
                            <p>🕐 <strong>Kết thúc:</strong> {event_end.strftime('%d/%m/%Y %H:%M')}</p>
                            <p>📍 <strong>Địa điểm:</strong> {event['location'] if event['location'] else 'Không có'}</p>
                            <p>⏰ <strong>Nhắc trước:</strong> {event['time_reminder']} phút</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        if st.button("🗑️", key=f"delete_{event['id']}", help="Xóa sự kiện"):
                            delete_event(event['id'], st.session_state.user_id)
                            st.success("✅ Đã xóa sự kiện!")
                            st.rerun()
                    
                    st.divider()
        else:
            st.info(f"📭 Không có sự kiện nào {filter_option.lower()}")
    else:
        st.info("📭 Bạn chưa có sự kiện nào. Hãy thêm sự kiện mới!")
