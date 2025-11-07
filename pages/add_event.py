"""
Trang thêm sự kiện mới với NLP
"""
import streamlit as st
from datetime import datetime
from utils.database import add_event

def add_event_page():
    """Trang thêm sự kiện (dùng trong dialog)"""
    # Nút đóng dialog
    col1, col2 = st.columns([5, 1])
    with col2:
        if st.button("✖️ Đóng", key="close_dialog_top"):
            st.session_state.show_add_dialog = False
            st.session_state.nlp_result = None
            st.rerun()
    
    st.markdown("""
        <div style='background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%); 
                    padding: 1.5rem; border-radius: 15px; margin-bottom: 1.5rem; text-align: center;'>
            <p style='color: #718096; margin: 0; font-size: 0.95rem;'>
                💡 Nhập bằng ngôn ngữ tự nhiên - AI sẽ tự động phân tích
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <div style='background: white; padding: 1rem; border-radius: 10px; margin-bottom: 1rem; 
                    border-left: 4px solid #667eea;'>
            <p style='color: #4a5568; margin: 0; font-size: 0.9rem;'>
                <strong>💬 Ví dụ:</strong><br/>
                • "Họp team vào lúc 9h30 ngày mai tại phòng A101 nhắc trước 15 phút"<br/>
                • "Nhắc tôi học bài lúc 14:00 ngày 10/11"<br/>
                • "Đi chơi tối thứ 7 này lúc 8 giờ"
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    natural_input = st.text_area(
        "📝 Mô tả sự kiện của bạn:",
        placeholder="Nhập mô tả sự kiện...",
        height=120,
        help="Nhập bằng tiếng Việt tự nhiên, AI sẽ tự động phân tích thời gian, địa điểm, nhắc nhở"
    )
    
    if st.button("🔍 Phân tích", use_container_width=True, type="primary"):
        if natural_input:
            with st.spinner("Đang phân tích..."):
                result = st.session_state.nlp_processor.process_text(natural_input)
                
                if result.get('success'):
                    st.session_state.nlp_result = result
                    st.success("✅ Phân tích thành công!")
                else:
                    st.error(f"❌ Lỗi: {result.get('error', 'Không thể phân tích văn bản')}")
        else:
            st.warning("⚠️ Vui lòng nhập mô tả sự kiện!")
    
    # Form chỉnh sửa sau khi phân tích
    if st.session_state.nlp_result:
        st.divider()
        st.markdown("""
            <div style='background: linear-gradient(135deg, #48bb7815 0%, #00d4ff15 100%); 
                        padding: 1.5rem; border-radius: 15px; margin: 1.5rem 0;'>
                <h3 style='color: #2d3748; margin: 0;'>✏️ Kiểm tra và chỉnh sửa thông tin</h3>
                <p style='color: #718096; margin: 0.5rem 0 0 0;'>Xem lại và điều chỉnh nếu cần</p>
            </div>
        """, unsafe_allow_html=True)
        
        result = st.session_state.nlp_result
        
        with st.form("edit_event_form"):
            event_name = st.text_input("Tên sự kiện:", value=result.get('event_name', ''))
            
            col1, col2 = st.columns(2)
            with col1:
                start_time_str = result.get('start_time', '')
                if start_time_str:
                    start_dt = datetime.strptime(start_time_str, '%Y-%m-%d %H:%M:%S')
                    start_date = st.date_input("Ngày bắt đầu:", value=start_dt.date())
                    start_time = st.text_input("Giờ bắt đầu (HH:MM):", value=start_dt.strftime('%H:%M'))
                else:
                    start_date = st.date_input("Ngày bắt đầu:")
                    start_time = st.text_input("Giờ bắt đầu (HH:MM):", value="09:00")
            
            with col2:
                end_time_str = result.get('end_time', '')
                if end_time_str:
                    end_dt = datetime.strptime(end_time_str, '%Y-%m-%d %H:%M:%S')
                    end_date = st.date_input("Ngày kết thúc:", value=end_dt.date())
                    end_time = st.text_input("Giờ kết thúc (HH:MM):", value=end_dt.strftime('%H:%M'))
                else:
                    end_date = st.date_input("Ngày kết thúc:", value=start_date if 'start_date' in locals() else None)
                    end_time = st.text_input("Giờ kết thúc (HH:MM):", value="10:00")
            
            location = st.text_input("Địa điểm:", value=result.get('location', '') or '')
            time_reminder = st.number_input("Nhắc trước (phút):", min_value=0, value=result.get('time_reminder', 15))
            
            col1, col2 = st.columns(2)
            with col1:
                save_button = st.form_submit_button("💾 Lưu sự kiện", use_container_width=True, type="primary")
            with col2:
                cancel_button = st.form_submit_button("❌ Hủy", use_container_width=True)
            
            if save_button:
                try:
                    # Tạo datetime từ form
                    start_datetime = datetime.strptime(f"{start_date} {start_time}", '%Y-%m-%d %H:%M')
                    end_datetime = datetime.strptime(f"{end_date} {end_time}", '%Y-%m-%d %H:%M')
                    
                    # Validate
                    if not event_name:
                        st.error("❌ Tên sự kiện không được để trống!")
                    elif end_datetime <= start_datetime:
                        st.error("❌ Thời gian kết thúc phải sau thời gian bắt đầu!")
                    else:
                        # Lưu vào database
                        add_event(
                            st.session_state.user_id,
                            event_name,
                            start_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                            end_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                            location if location else None,
                            time_reminder
                        )
                        
                        st.success("✅ Đã lưu sự kiện thành công!")
                        st.session_state.nlp_result = None
                        st.session_state.show_add_dialog = False
                        st.rerun()
                        
                except ValueError as e:
                    st.error(f"❌ Lỗi định dạng thời gian: {e}")
            
            if cancel_button:
                st.session_state.nlp_result = None
                st.session_state.show_add_dialog = False
                st.rerun()
