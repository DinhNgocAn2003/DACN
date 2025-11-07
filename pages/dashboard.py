"""
Dashboard chính
"""
import streamlit as st
import os
from utils.session import load_saved_login, clear_saved_login
from utils.database import get_upcoming_events
from pages.add_event import add_event_page
from pages.calendar_view import calendar_page
from pages.events_list import events_list_page

def dashboard_page():
    """Trang dashboard chính"""
    # Hiển thị thông báo tự động đăng nhập (chỉ 1 lần)
    if not st.session_state.auto_login_shown:
        saved = load_saved_login()
        if saved:
            st.success(f"✅ Tự động đăng nhập thành công! Xin chào {st.session_state.username} 👋")
            st.session_state.auto_login_shown = True
    
    # Header đẹp hơn
    col1, col2, col3 = st.columns([1, 6, 1])
    with col2:
        st.markdown(f"""
            <div style='text-align: center; padding: 1rem 0; margin-bottom: 1rem;'>
                <h1 class='welcome-header'>
                    Xin chào, <span style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>{st.session_state.username}</span>!
                </h1>
                <p style='color: #718096; font-size: 1rem; margin-top: -0.5rem;'>
                    Hôm nay bạn có {len(get_upcoming_events(st.session_state.user_id, hours=24))} sự kiện sắp diễn ra
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        if st.button("🚪 Đăng xuất", use_container_width=True):
            clear_saved_login()  # Xóa phiên đăng nhập đã lưu
            st.session_state.logged_in = False
            st.session_state.user_id = None
            st.session_state.username = None
            st.session_state.auto_login_shown = False
            st.rerun()
    
    # Get upcoming events and push to JavaScript
    upcoming_events = get_upcoming_events(st.session_state.user_id, hours=24)
    
    events_js = []
    if upcoming_events:
        for event in upcoming_events:
            events_js.append({
                'id': str(event['id']),
                'name': event['event_name'],
                'start_time': event['start_time'],
                'location': event['location'],
                'reminder_minutes': event['time_reminder'] or 15
            })
    
    # Load notification component
    notification_html_path = os.path.join(os.path.dirname(__file__), '..', 'notification_component.html')
    if os.path.exists(notification_html_path):
        with open(notification_html_path, 'r', encoding='utf-8') as f:
            notification_html = f.read()
        
        # Inject events data
        notification_html = notification_html.replace('</body>', f"""
        <script>
        window.upcomingEvents = {events_js};
        </script>
        </body>
        """)
        
        st.components.v1.html(notification_html, height=0)
    
    # Button để mở dialog thêm sự kiện - Tinh tế hơn
    col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 2])
    with col3:
        if st.button("➕ Thêm Sự Kiện", use_container_width=True, type="primary"):
            st.session_state.show_add_dialog = True
    
    # Dialog thêm sự kiện
    if 'show_add_dialog' not in st.session_state:
        st.session_state.show_add_dialog = False
    
    if st.session_state.show_add_dialog:
        add_event_dialog()
    
    st.divider()
    
    # Tabs cho calendar và danh sách
    tab1, tab2 = st.tabs(["📅 Lịch Tháng", "📋 Danh Sách Sự Kiện"])
    
    with tab1:
        calendar_page()
    
    with tab2:
        events_list_page()

@st.dialog("✨ Thêm Sự Kiện Mới", width="large")
def add_event_dialog():
    """Dialog thêm sự kiện"""
    add_event_page()
