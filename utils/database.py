"""
Các hàm xử lý database
"""
import sqlite3
import bcrypt
import os
from datetime import datetime

def get_db_connection():
    """Kết nối đến database"""
    db_path = os.path.join('personal_calendar', 'database.db')
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def register_user(username, email, password):
    """Đăng ký người dùng mới"""
    conn = get_db_connection()
    c = conn.cursor()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    try:
        c.execute('''INSERT INTO users (username, email, password) 
                     VALUES (?, ?, ?)''', (username, email, hashed_password))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False

def verify_user(username, password):
    """Xác thực người dùng"""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT id, password FROM users WHERE username = ?', (username,))
    user = c.fetchone()
    conn.close()
    
    if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
        return user['id']
    return None

def add_event(user_id, event_name, start_time, end_time, location, time_reminder):
    """Thêm sự kiện mới"""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''INSERT INTO events (user_id, event_name, start_time, end_time, location, time_reminder)
                 VALUES (?, ?, ?, ?, ?, ?)''',
              (user_id, event_name, start_time, end_time, location, time_reminder))
    conn.commit()
    conn.close()

def get_events(user_id):
    """Lấy danh sách sự kiện của người dùng"""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''SELECT * FROM events WHERE user_id = ? 
                 ORDER BY start_time ASC''', (user_id,))
    events = [dict(row) for row in c.fetchall()]
    conn.close()
    return events

def update_event(event_id, event_name, start_time, end_time, location, time_reminder):
    """Cập nhật thông tin sự kiện"""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''UPDATE events 
                 SET event_name = ?, start_time = ?, end_time = ?, location = ?, time_reminder = ?
                 WHERE id = ?''',
              (event_name, start_time, end_time, location, time_reminder, event_id))
    conn.commit()
    conn.close()

def delete_event(event_id, user_id):
    """Xóa sự kiện"""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('DELETE FROM events WHERE id = ? AND user_id = ?', (event_id, user_id))
    conn.commit()
    conn.close()

def get_upcoming_events(user_id, hours=24):
    """Lấy các sự kiện sắp diễn ra trong vòng X giờ tới"""
    from datetime import timedelta
    conn = get_db_connection()
    c = conn.cursor()
    now = datetime.now()
    future = now + timedelta(hours=hours)
    
    c.execute('''SELECT * FROM events 
                 WHERE user_id = ? AND start_time BETWEEN ? AND ?
                 ORDER BY start_time ASC''',
              (user_id, now.strftime('%Y-%m-%d %H:%M:%S'), future.strftime('%Y-%m-%d %H:%M:%S')))
    events = [dict(row) for row in c.fetchall()]
    conn.close()
    return events
