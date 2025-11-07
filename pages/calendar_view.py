# -*- coding: utf-8 -*-
import streamlit as st
from datetime import datetime
import calendar as cal_module
from utils.database import get_events, delete_event, update_event

@st.dialog('Sự kiện trong ngày', width='large')
def show_day_events_dialog(selected_date, events_on_date):
    days = ['Thứ 2', 'Thứ 3', 'Thứ 4', 'Thứ 5', 'Thứ 6', 'Thứ 7', 'Chủ Nhật']
    day_name = days[selected_date.weekday()]
    
    st.markdown(f'''
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
               padding: 1rem; border-radius: 12px; color: white; margin-bottom: 1rem;">
        <h3 style="margin: 0;"> {day_name}, {selected_date.strftime('%d/%m/%Y')}</h3>
        <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">{len(events_on_date)} sự kiện</p>
    </div>
    ''', unsafe_allow_html=True)
    
    if not events_on_date:
        st.info('Không có sự kiện nào trong ngày này')
    else:
        for i, event in enumerate(events_on_date):
            with st.expander(f"{event['event_name']}", expanded=(i==0)):
                start_time = datetime.strptime(event['start_time'], '%Y-%m-%d %H:%M:%S')
                end_time = datetime.strptime(event['end_time'], '%Y-%m-%d %H:%M:%S')
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**Thời gian:** {start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}")
                    if event['location']:
                        st.write(f"**Địa điểm:** {event['location']}")
                    st.write(f"**Nhắc trước:** {event['time_reminder']} phút")
                
                with col2:
                    if st.button('Sửa', key=f"edit_{event['id']}", use_container_width=True):
                        st.session_state.editing_event = event
                        st.rerun()
                    
                    if st.button('Xóa', key=f"del_{event['id']}", type='secondary', use_container_width=True):
                        delete_event(event['id'], st.session_state.user_id)
                        st.success('Đã xóa sự kiện!')
                        st.rerun()

@st.dialog('Chỉnh sửa sự kiện', width='large')
def edit_event_dialog(event):
    st.markdown('### Chỉnh sửa thông tin')
    
    start_time = datetime.strptime(event['start_time'], '%Y-%m-%d %H:%M:%S')
    end_time = datetime.strptime(event['end_time'], '%Y-%m-%d %H:%M:%S')
    
    event_name = st.text_input('Tên sự kiện', value=event['event_name'])
    
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input('Ngày bắt đầu', value=start_time.date())
        start_time_input = st.text_input('Giờ bắt đầu (HH:MM)', value=start_time.strftime('%H:%M'))
    
    with col2:
        end_date = st.date_input('Ngày kết thúc', value=end_time.date())
        end_time_input = st.text_input('Giờ kết thúc (HH:MM)', value=end_time.strftime('%H:%M'))
    
    location = st.text_input('Địa điểm', value=event['location'] or '')
    time_reminder = st.number_input('Nhắc trước (phút)', min_value=0, value=event['time_reminder'])
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button('Lưu thay đổi', type='primary', use_container_width=True):
            try:
                start_hour, start_min = map(int, start_time_input.split(':'))
                end_hour, end_min = map(int, end_time_input.split(':'))
                
                new_start = datetime.combine(start_date, datetime.min.time()).replace(hour=start_hour, minute=start_min)
                new_end = datetime.combine(end_date, datetime.min.time()).replace(hour=end_hour, minute=end_min)
                
                update_event(
                    event['id'],
                    event_name,
                    new_start.strftime('%Y-%m-%d %H:%M:%S'),
                    new_end.strftime('%Y-%m-%d %H:%M:%S'),
                    location if location else None,
                    int(time_reminder)
                )
                
                st.success('Đã cập nhật sự kiện!')
                del st.session_state.editing_event
                st.rerun()
            except Exception as e:
                st.error(f'Lỗi: {str(e)}')
    
    with col2:
        if st.button('Hủy', use_container_width=True):
            del st.session_state.editing_event
            st.rerun()

def calendar_page():
    events = get_events(st.session_state.user_id)
    
    if 'calendar_month' not in st.session_state:
        st.session_state.calendar_month = datetime.now().month
    if 'calendar_year' not in st.session_state:
        st.session_state.calendar_year = datetime.now().year
    
    st.markdown('''
        <div style='background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%); 
                    padding: 1.5rem; border-radius: 20px; margin-bottom: 1.5rem; text-align: center;'>
            <h2 style='color: #2d3748; margin: 0; font-size: 2rem;'> Lịch Tháng</h2>
            <p style='color: #718096; margin: 0.5rem 0 0 0;'>Xem tổng quan sự kiện theo tháng</p>
        </div>
    ''', unsafe_allow_html=True)
    
    col1, col2, col3, col4, col5, col6, col7 = st.columns([1, 1, 1, 2, 1, 1, 1])
    
    with col1:
        if st.button('⏮️ Năm trước', key='prev_year', help='Năm trước'):
            st.session_state.calendar_year -= 1
            st.rerun()
    
    with col2:
        if st.button('◀️ Tháng trước', key='prev_month', help='Tháng trước'):
            if st.session_state.calendar_month == 1:
                st.session_state.calendar_month = 12
                st.session_state.calendar_year -= 1
            else:
                st.session_state.calendar_month -= 1
            st.rerun()
    
    with col4:
        if st.button('📅 Hôm nay', use_container_width=True, type='primary'):
            now = datetime.now()
            st.session_state.calendar_month = now.month
            st.session_state.calendar_year = now.year
            st.rerun()
    
    with col6:
        if st.button('Tháng sau ▶️', key='next_month', help='Tháng sau'):
            if st.session_state.calendar_month == 12:
                st.session_state.calendar_month = 1
                st.session_state.calendar_year += 1
            else:
                st.session_state.calendar_month += 1
            st.rerun()
    
    with col7:
        if st.button('Năm sau ⏭️', key='next_year', help='Năm sau'):
            st.session_state.calendar_year += 1
            st.rerun()
    
    current_month = st.session_state.calendar_month
    current_year = st.session_state.calendar_year
    now = datetime.now()
    
    event_dates = {}
    for event in events:
        event_start = datetime.strptime(event['start_time'], '%Y-%m-%d %H:%M:%S')
        event_date = event_start.date()
        if event_date not in event_dates:
            event_dates[event_date] = []
        event_dates[event_date].append(event['event_name'])
    
    cal = cal_module.monthcalendar(current_year, current_month)
    month_name = cal_module.month_name[current_month]
    
    today = now.date()
    events_by_date = {}
    for date_obj in event_dates.keys():
        day_events = [e for e in events if datetime.strptime(e['start_time'], '%Y-%m-%d %H:%M:%S').date() == date_obj]
        events_by_date[date_obj.strftime('%Y-%m-%d')] = day_events
    
    # CSS và HTML cho calendar
    calendar_css = """
    <style>
        .calendar-container {
            background: linear-gradient(135deg, #ffffff 0%, #f7fafc 100%);
            border-radius: 15px;
            padding: 1.5rem;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            border: 1px solid #e2e8f0;
            max-width: 900px;
            margin: 0 auto;
        }
        .calendar-header {
            text-align: center;
            font-size: 1.4rem;
            font-weight: 600;
            margin-bottom: 1rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            padding: 0.3rem;
        }
        .calendar-table {
            width: 100%;
            border-collapse: separate;
            border-spacing: 6px;
        }
        .calendar-table th {
            padding: 8px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            font-weight: 500;
            text-align: center;
            border-radius: 8px;
            font-size: 0.85rem;
        }
        .calendar-table td {
            padding: 8px;
            text-align: center;
            background: white;
            border-radius: 10px;
            transition: all 0.2s;
            position: relative;
            height: 60px;
            width: 60px;
            vertical-align: top;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            cursor: pointer;
        }
        .calendar-table td:hover {
            transform: scale(1.05);
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }
        .calendar-table td.empty {
            background: transparent;
            box-shadow: none;
            cursor: default;
        }
        .calendar-table td.empty:hover {
            transform: none;
        }
        .calendar-table td.today {
            background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
            box-shadow: 0 2px 6px rgba(72, 187, 120, 0.3);
            border: 3px solid #2f855a;
        }
        .calendar-table td.today .day-number {
            color: white;
            font-weight: 700;
        }
        .calendar-table td.has-event {
            background: linear-gradient(135deg, #ff9a56 0%, #ff6b35 100%);
            border: 2px solid #ff6b35;
        }
        .calendar-table td.has-event .day-number {
            color: white;
            font-weight: 600;
        }
        .calendar-table td.has-event .event-dot {
            background: white;
        }
        .calendar-table td.has-event .event-count {
            color: white;
        }
        /* Hôm nay VÀ có sự kiện - Hiển thị cả 2 màu */
        .calendar-table td.today.has-event {
            background: linear-gradient(135deg, #ff9a56 0%, #ff6b35 100%);
            border: 4px solid #48bb78;
            box-shadow: 0 4px 12px rgba(72, 187, 120, 0.6), 0 0 0 2px #2f855a;
            position: relative;
        }
        .calendar-table td.today.has-event::before {
            content: '🟢';
            position: absolute;
            top: 2px;
            left: 2px;
            font-size: 10px;
        }
        .day-number {
            font-size: 1rem;
            font-weight: 500;
            color: #2d3748;
            margin-bottom: 2px;
        }
        .event-dot {
            display: inline-block;
            width: 6px;
            height: 6px;
            background: #667eea;
            border-radius: 50%;
            margin: 1px;
        }
        .event-count {
            font-size: 0.7rem;
            color: #667eea;
            font-weight: 600;
            margin-top: 2px;
        }
    </style>
    """
    
    st.markdown(calendar_css, unsafe_allow_html=True)
    
    # Tạo HTML calendar với onclick
    calendar_html = f"""
    <div class="calendar-container">
        <div class="calendar-header">{month_name} {current_year}</div>
        <table class="calendar-table">
            <tr>
                <th>Thứ 2</th>
                <th>Thứ 3</th>
                <th>Thứ 4</th>
                <th>Thứ 5</th>
                <th>Thứ 6</th>
                <th>Thứ 7</th>
                <th>Chủ Nhật</th>
            </tr>
    """
    
    for week in cal:
        calendar_html += "<tr>"
        for day in week:
            if day == 0:
                calendar_html += '<td class="empty"></td>'
            else:
                date_obj = datetime(current_year, current_month, day).date()
                classes = []
                
                if date_obj == today:
                    classes.append("today")
                
                if date_obj in event_dates:
                    classes.append("has-event")
                
                class_str = ' '.join(classes)
                date_str = date_obj.strftime('%Y-%m-%d')
                
                calendar_html += f'<td class="{class_str}" onclick="selectDate(\'{date_str}\')">'
                calendar_html += f'<div class="day-number">{day}</div>'
                
                if date_obj in event_dates:
                    num_events = len(event_dates[date_obj])
                    if num_events <= 2:
                        for _ in range(num_events):
                            calendar_html += '<span class="event-dot"></span>'
                    else:
                        calendar_html += f'<div class="event-count">📌 {num_events}</div>'
                
                calendar_html += '</td>'
        calendar_html += "</tr>"
    
    calendar_html += """
        </table>
    </div>
    <script>
        function selectDate(dateStr) {
            // Send message to Streamlit
            window.parent.postMessage({
                type: 'streamlit:setComponentValue',
                data: dateStr
            }, '*');
        }
    </script>
    """
    
    st.markdown(calendar_html, unsafe_allow_html=True)
    
    # Hướng dẫn người dùng
    st.info("💡 Click vào ngày bất kỳ trên lịch để xem chi tiết sự kiện")
    
    # Danh sách ngày có sự kiện trong tháng này để click
    dates_in_month = sorted([d for d in event_dates.keys() if d.month == current_month and d.year == current_year])
    
    if dates_in_month:
        st.markdown("### 📋 Ngày có sự kiện:")
        cols = st.columns(7)
        for idx, date in enumerate(dates_in_month):
            with cols[idx % 7]:
                num_events = len(event_dates[date])
                day_name = ['T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'CN'][date.weekday()]
                if st.button(f"{date.day}/{date.month}\n{day_name} ({num_events})", 
                           key=f'event_date_{date}', 
                           use_container_width=True,
                           type='secondary'):
                    st.session_state.selected_calendar_date = date
                    st.rerun()
    
    if 'editing_event' in st.session_state:
        edit_event_dialog(st.session_state.editing_event)
    
    elif 'selected_calendar_date' in st.session_state:
        selected_date = st.session_state.selected_calendar_date
        date_str = selected_date.strftime('%Y-%m-%d')
        events_on_date = events_by_date.get(date_str, [])
        
        show_day_events_dialog(selected_date, events_on_date)
        
        del st.session_state.selected_calendar_date
