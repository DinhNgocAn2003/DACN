import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import sqlite3
import os

# Cấu hình email (Gmail)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "your-email@gmail.com"  # Thay đổi email của bạn
SENDER_PASSWORD = "your-app-password"  # App password của Gmail

def get_db_connection():
    """Kết nối đến database"""
    db_path = os.path.join('personal_calendar', 'database.db')
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def get_user_email(user_id):
    """Lấy email của user"""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT email FROM users WHERE id = ?', (user_id,))
    user = c.fetchone()
    conn.close()
    return user['email'] if user else None

def get_upcoming_events_for_user(user_id, hours=24):
    """Lấy sự kiện sắp tới của user"""
    conn = get_db_connection()
    c = conn.cursor()
    
    now = datetime.now()
    future = now + timedelta(hours=hours)
    
    c.execute('''
        SELECT id, event_name, start_time, end_time, location, time_reminder 
        FROM events 
        WHERE user_id = ? 
        AND datetime(start_time) >= datetime(?)
        AND datetime(start_time) <= datetime(?)
        ORDER BY start_time
    ''', (user_id, now.strftime('%Y-%m-%d %H:%M:%S'), future.strftime('%Y-%m-%d %H:%M:%S')))
    
    events = c.fetchall()
    conn.close()
    return events

def send_event_reminder_email(user_id, event):
    """Gửi email nhắc nhở sự kiện"""
    try:
        # Lấy email người dùng
        user_email = get_user_email(user_id)
        if not user_email:
            print(f"Không tìm thấy email cho user_id: {user_id}")
            return False
        
        # Parse thời gian
        start_time = datetime.strptime(event['start_time'], '%Y-%m-%d %H:%M:%S')
        
        # Tạo nội dung email
        subject = f"📅 Nhắc nhở: {event['event_name']}"
        
        html_content = f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    background: #f9f9f9;
                    border-radius: 10px;
                }}
                .header {{
                    background: #1f77b4;
                    color: white;
                    padding: 20px;
                    text-align: center;
                    border-radius: 10px 10px 0 0;
                }}
                .content {{
                    background: white;
                    padding: 30px;
                    border-radius: 0 0 10px 10px;
                }}
                .event-info {{
                    background: #e3f2fd;
                    padding: 15px;
                    border-left: 4px solid #1f77b4;
                    margin: 20px 0;
                }}
                .info-row {{
                    margin: 10px 0;
                }}
                .label {{
                    font-weight: bold;
                    color: #1f77b4;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 20px;
                    color: #666;
                    font-size: 0.9em;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📅 Lịch Cá Nhân</h1>
                    <p>Nhắc nhở sự kiện</p>
                </div>
                <div class="content">
                    <h2>🔔 Bạn có sự kiện sắp tới!</h2>
                    <div class="event-info">
                        <div class="info-row">
                            <span class="label">📌 Sự kiện:</span> {event['event_name']}
                        </div>
                        <div class="info-row">
                            <span class="label">🕐 Thời gian bắt đầu:</span> {start_time.strftime('%d/%m/%Y %H:%M')}
                        </div>
                        {f'<div class="info-row"><span class="label">📍 Địa điểm:</span> {event["location"]}</div>' if event['location'] else ''}
                        <div class="info-row">
                            <span class="label">⏰ Nhắc trước:</span> {event['time_reminder']} phút
                        </div>
                    </div>
                    <p>Đừng quên tham gia sự kiện đúng giờ nhé! 😊</p>
                    <div class="footer">
                        <p>Email này được gửi tự động từ hệ thống Lịch Cá Nhân</p>
                        <p>© 2025 Personal Calendar</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Tạo email
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = SENDER_EMAIL
        message["To"] = user_email
        
        # Thêm nội dung HTML
        html_part = MIMEText(html_content, "html")
        message.attach(html_part)
        
        # Gửi email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(message)
        
        print(f"✅ Đã gửi email nhắc nhở đến {user_email} cho sự kiện: {event['event_name']}")
        return True
        
    except Exception as e:
        print(f"❌ Lỗi gửi email: {e}")
        return False

def send_daily_summary_email(user_id):
    """Gửi email tổng hợp sự kiện trong ngày"""
    try:
        user_email = get_user_email(user_id)
        if not user_email:
            return False
        
        # Lấy sự kiện trong 24h tới
        events = get_upcoming_events_for_user(user_id, hours=24)
        
        if not events:
            print(f"Không có sự kiện nào trong 24h tới cho user_id: {user_id}")
            return False
        
        # Tạo nội dung email
        subject = f"📅 Tổng hợp sự kiện hôm nay - {datetime.now().strftime('%d/%m/%Y')}"
        
        events_html = ""
        for idx, event in enumerate(events, 1):
            start_time = datetime.strptime(event['start_time'], '%Y-%m-%d %H:%M:%S')
            location_html = f'<div><span class="label">📍 Địa điểm:</span> {event["location"]}</div>' if event['location'] else ''
            
            events_html += f"""
            <div class="event-item">
                <h3>{idx}. {event['event_name']}</h3>
                <div><span class="label">🕐 Thời gian:</span> {start_time.strftime('%H:%M - %d/%m/%Y')}</div>
                {location_html}
            </div>
            """
        
        html_content = f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    background: #f9f9f9;
                }}
                .header {{
                    background: #1f77b4;
                    color: white;
                    padding: 20px;
                    text-align: center;
                    border-radius: 10px;
                }}
                .event-item {{
                    background: white;
                    padding: 20px;
                    margin: 15px 0;
                    border-left: 4px solid #1f77b4;
                    border-radius: 5px;
                }}
                .label {{
                    font-weight: bold;
                    color: #1f77b4;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 30px;
                    color: #666;
                    font-size: 0.9em;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📅 Lịch của bạn hôm nay</h1>
                </div>
                <div style="margin-top: 20px;">
                    <p>Xin chào! Bạn có <strong>{len(events)} sự kiện</strong> trong 24 giờ tới:</p>
                    {events_html}
                </div>
                <div class="footer">
                    <p>Chúc bạn một ngày làm việc hiệu quả! 💪</p>
                    <p>© 2025 Personal Calendar</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = SENDER_EMAIL
        message["To"] = user_email
        
        html_part = MIMEText(html_content, "html")
        message.attach(html_part)
        
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(message)
        
        print(f"✅ Đã gửi email tổng hợp đến {user_email}")
        return True
        
    except Exception as e:
        print(f"❌ Lỗi gửi email tổng hợp: {e}")
        return False

def check_and_send_reminders():
    """Kiểm tra và gửi email nhắc nhở cho tất cả users"""
    conn = get_db_connection()
    c = conn.cursor()
    
    # Lấy tất cả users
    c.execute('SELECT id FROM users')
    users = c.fetchall()
    conn.close()
    
    for user in users:
        user_id = user['id']
        events = get_upcoming_events_for_user(user_id, hours=24)
        
        for event in events:
            start_time = datetime.strptime(event['start_time'], '%Y-%m-%d %H:%M:%S')
            reminder_minutes = event['time_reminder'] or 15
            reminder_time = start_time - timedelta(minutes=reminder_minutes)
            now = datetime.now()
            
            # Kiểm tra nếu đã đến thời gian nhắc nhở (trong khoảng 5 phút)
            time_diff = (reminder_time - now).total_seconds() / 60
            
            if -5 <= time_diff <= 5:  # Trong khoảng 5 phút trước/sau thời gian nhắc
                send_event_reminder_email(user_id, event)

if __name__ == "__main__":
    print("🔍 Kiểm tra và gửi email nhắc nhở...")
    check_and_send_reminders()
