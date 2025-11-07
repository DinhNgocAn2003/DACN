"""
Quản lý session và cookie
"""
import json
import os
from datetime import datetime

def save_login(user_id, username):
    """Lưu phiên đăng nhập"""
    login_file = 'saved_login.json'
    data = {
        'user_id': user_id,
        'username': username,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    with open(login_file, 'w') as f:
        json.dump(data, f)

def load_saved_login():
    """Load phiên đăng nhập đã lưu"""
    login_file = 'saved_login.json'
    if os.path.exists(login_file):
        try:
            with open(login_file, 'r') as f:
                data = json.load(f)
                # Kiểm tra phiên đăng nhập không quá 7 ngày
                saved_time = datetime.strptime(data['timestamp'], '%Y-%m-%d %H:%M:%S')
                if (datetime.now() - saved_time).days < 7:
                    return data
        except:
            pass
    return None

def clear_saved_login():
    """Xóa phiên đăng nhập đã lưu"""
    login_file = 'saved_login.json'
    if os.path.exists(login_file):
        os.remove(login_file)
