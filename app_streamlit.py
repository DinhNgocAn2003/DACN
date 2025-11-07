"""
Ứng dụng Lịch Cá Nhân
File chính để khởi chạy ứng dụng
"""
import streamlit as st
from personal_calendar.nlp_processor import NLPProcessor
from utils.session import load_saved_login
from pages.auth import login_page
from pages.dashboard import dashboard_page

# Cấu hình trang
st.set_page_config(
    page_title="Lịch Cá Nhân",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS tùy chỉnh - Thiết kế đẹp hơn
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
    
    /* Global styles */
    .main {
        font-family: 'Poppins', sans-serif;
    }
    
    /* Header styles */
    .main-header {
        font-size: 2.8rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        margin-bottom: 2rem;
        padding: 1rem 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    .welcome-header {
        font-size: 2.2rem;
        font-weight: 600;
        color: #2d3748;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Card styles */
    .event-card {
        background: linear-gradient(135deg, #ffffff 0%, #f7fafc 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin-bottom: 1.5rem;
        border-left: 5px solid #667eea;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07), 0 1px 3px rgba(0, 0, 0, 0.06);
        transition: all 0.3s ease;
    }
    
    .event-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1), 0 3px 6px rgba(0, 0, 0, 0.08);
    }
    
    .event-card h3 {
        color: #2d3748;
        font-weight: 600;
        margin-bottom: 0.8rem;
        font-size: 1.3rem;
    }
    
    .event-card p {
        color: #4a5568;
        margin: 0.5rem 0;
        font-size: 0.95rem;
    }
    
    /* Info box styles */
    .info-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(102, 126, 234, 0.3);
    }
    
    .info-box h3 {
        margin: 0 0 0.5rem 0;
        font-weight: 600;
    }
    
    /* Button enhancement */
    .stButton > button {
        border-radius: 10px;
        font-weight: 500;
        transition: all 0.3s ease;
        border: none;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
    }
    
    /* Tab styles */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #f7fafc;
        padding: 0.5rem;
        border-radius: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    /* Form styles */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        border-radius: 10px;
        border: 2px solid #e2e8f0;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Divider */
    hr {
        margin: 2rem 0;
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, #667eea, transparent);
    }
    
    /* Success/Error messages */
    .stSuccess, .stError, .stWarning, .stInfo {
        border-radius: 10px;
        font-weight: 500;
    }
    
    /* Hide Sidebar completely */
    [data-testid="stSidebar"] {
        display: none;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Animation */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .element-container {
        animation: fadeIn 0.5s ease-out;
    }

    /* Reduce top spacing: pull content closer to top */
    .block-container {
        padding-top: 0rem !important;
        margin-top: -20px !important;
    }

    /* Additional selectors to cover Streamlit structural changes */
    .stApp .main > div {
        padding-top: 0rem !important;
        margin-top: -20px !important;
    }
</style>
""", unsafe_allow_html=True)

# JavaScript cho Web Notifications
notification_script = """
<script>
// Request notification permission
if ('Notification' in window && Notification.permission === 'default') {
    Notification.requestPermission();
}

// Function to check upcoming events and send notifications
function checkUpcomingEvents() {
    // Get events from Streamlit (will be populated)
    const events = window.upcomingEvents || [];
    
    events.forEach(event => {
        const now = new Date();
        const eventTime = new Date(event.start_time);
        const reminderTime = new Date(eventTime.getTime() - event.reminder_minutes * 60000);
        
        // Check if it's time to remind
        if (now >= reminderTime && now < eventTime && !event.notified) {
            if (Notification.permission === 'granted') {
                const notification = new Notification('📅 Nhắc nhở sự kiện', {
                    body: `${event.name} sẽ bắt đầu lúc ${eventTime.toLocaleTimeString('vi-VN')}` + 
                          (event.location ? ` tại ${event.location}` : ''),
                    icon: '📅',
                    badge: '📅',
                    tag: event.id,
                    requireInteraction: true
                });
                
                notification.onclick = function() {
                    window.focus();
                    this.close();
                };
                
                // Mark as notified
                event.notified = true;
            }
        }
    });
}

// Check every minute
setInterval(checkUpcomingEvents, 60000);
// Check immediately
checkUpcomingEvents();
</script>
"""

st.markdown(notification_script, unsafe_allow_html=True)

# === SESSION STATE ===
# Kiểm tra phiên đăng nhập đã lưu trước
saved_login = load_saved_login()

if 'logged_in' not in st.session_state:
    if saved_login:
        st.session_state.logged_in = True
        st.session_state.user_id = saved_login['user_id']
        st.session_state.username = saved_login['username']
    else:
        st.session_state.logged_in = False
        st.session_state.user_id = None
        st.session_state.username = None
else:
    # Nếu đã có session nhưng chưa có user_id, thử load từ saved login
    if not st.session_state.get('user_id') and saved_login:
        st.session_state.logged_in = True
        st.session_state.user_id = saved_login['user_id']
        st.session_state.username = saved_login['username']
        
if 'user_id' not in st.session_state:
    if saved_login:
        st.session_state.user_id = saved_login['user_id']
    else:
        st.session_state.user_id = None
        
if 'username' not in st.session_state:
    if saved_login:
        st.session_state.username = saved_login['username']
    else:
        st.session_state.username = None

if 'nlp_processor' not in st.session_state:
    st.session_state.nlp_processor = NLPProcessor()
if 'nlp_result' not in st.session_state:
    st.session_state.nlp_result = None
if 'auto_login_shown' not in st.session_state:
    st.session_state.auto_login_shown = False

# === MAIN APP ===
def main():
    if not st.session_state.logged_in:
        login_page()
    else:
        dashboard_page()

if __name__ == "__main__":
    main()
