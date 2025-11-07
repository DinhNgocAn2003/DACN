"""
Trang đăng nhập và đăng ký
"""
import streamlit as st
from utils.database import register_user, verify_user
from utils.session import save_login, clear_saved_login

def login_page():
    """Trang đăng nhập"""
    # Header với animation
    st.markdown("""
        <div style='text-align: center; padding: 2rem 0;'>
            <h1 class='main-header'>Lịch Cá Nhân Thông Minh</h1>
            <p style='color: #718096; font-size: 1.1rem; margin-top: -1rem;'>
                Quản lý thời gian hiệu quả với AI
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🔐 Đăng Nhập", "✨ Đăng Ký"])
    
    with tab1:
        st.markdown("""
            <div style='background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%); 
                        padding: 1.5rem; border-radius: 15px; margin-bottom: 1rem;'>
                <h3 style='color: #2d3748; margin: 0;'>🔐 Đăng nhập vào tài khoản</h3>
                <p style='color: #718096; margin: 0.5rem 0 0 0;'>Chào mừng bạn quay trở lại!</p>
            </div>
        """, unsafe_allow_html=True)
        with st.form("login_form"):
            username = st.text_input("Tên đăng nhập")
            password = st.text_input("Mật khẩu", type="password")
            remember_me = st.checkbox("🔒 Ghi nhớ đăng nhập (7 ngày)", value=True)
            
            col1, col2 = st.columns(2)
            with col1:
                submit = st.form_submit_button("Đăng nhập", use_container_width=True, type="primary")
            with col2:
                clear_login = st.form_submit_button("🗑️ Xóa phiên lưu", use_container_width=True)
            
            if clear_login:
                clear_saved_login()
                st.info("✅ Đã xóa phiên đăng nhập đã lưu")
            
            if submit:
                if username and password:
                    user_id = verify_user(username, password)
                    if user_id:
                        st.session_state.logged_in = True
                        st.session_state.user_id = user_id
                        st.session_state.username = username
                        
                        # Lưu phiên đăng nhập nếu chọn Remember Me
                        if remember_me:
                            save_login(user_id, username)
                            st.success("✅ Đăng nhập thành công! Đã lưu phiên đăng nhập.")
                        else:
                            clear_saved_login()
                            st.success("✅ Đăng nhập thành công!")
                        
                        st.rerun()
                    else:
                        st.error("❌ Tên đăng nhập hoặc mật khẩu không đúng!")
                else:
                    st.warning("⚠️ Vui lòng nhập đầy đủ thông tin!")
    
    with tab2:
        st.markdown("""
            <div style='background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%); 
                        padding: 1.5rem; border-radius: 15px; margin-bottom: 1rem;'>
                <h3 style='color: #2d3748; margin: 0;'>✨ Tạo tài khoản mới</h3>
                <p style='color: #718096; margin: 0.5rem 0 0 0;'>Bắt đầu quản lý thời gian hiệu quả hơn</p>
            </div>
        """, unsafe_allow_html=True)
        with st.form("register_form"):
            new_username = st.text_input("Tên đăng nhập mới")
            new_email = st.text_input("Email")
            new_password = st.text_input("Mật khẩu", type="password")
            confirm_password = st.text_input("Xác nhận mật khẩu", type="password")
            register = st.form_submit_button("Đăng ký", use_container_width=True)
            
            if register:
                if new_username and new_email and new_password and confirm_password:
                    if new_password != confirm_password:
                        st.error("❌ Mật khẩu xác nhận không khớp!")
                    elif len(new_password) < 6:
                        st.error("❌ Mật khẩu phải có ít nhất 6 ký tự!")
                    else:
                        if register_user(new_username, new_email, new_password):
                            st.success("✅ Đăng ký thành công! Hãy đăng nhập.")
                        else:
                            st.error("❌ Tên đăng nhập hoặc email đã tồn tại!")
                else:
                    st.warning("⚠️ Vui lòng nhập đầy đủ thông tin!")
