import os
import sys
import io
import smtplib
from email.message import EmailMessage
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from apscheduler.schedulers.background import BackgroundScheduler
from sqlmodel import Session, select
from dotenv import load_dotenv

from db import engine
from models import Event, User

# Cấu hình encoding
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
    except Exception:
        pass

# ======= CẤU HÌNH SMTP =======
load_dotenv()
SMTP_HOST = os.getenv("SMTP_HOST")
# Chỉ dùng cổng 465 (implicit SSL) cho SMTP
SMTP_PORT = 465
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
FROM_EMAIL = os.getenv("FROM_EMAIL")

REMINDER_INTERVAL = int(os.getenv("REMINDER_INTERVAL", "60"))

_scheduler: Optional[BackgroundScheduler] = None


def _send_email_smtp(to_email: str, subject: str, body: str) -> bool:
    # Gửi email bằng SMTP
    print(f"[debug] SMTP config: {SMTP_HOST}:{SMTP_PORT}, user: {SMTP_USER}")
    
    if not all([SMTP_HOST, SMTP_USER, SMTP_PASS]):
        print(f"[reminder] SMTP chưa cấu hình đầy đủ")
        return False

    msg = EmailMessage()
    msg["From"] = FROM_EMAIL
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)

    try:
        # Xử lý kết nối SMTP
        if SMTP_PORT == 465:
            # Port 465 dùng SSL implicit
            with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=30) as server:
                server.login(SMTP_USER, SMTP_PASS)
                server.send_message(msg)
        else:
            # Port 587 hoặc 25
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30) as server:
                # Thử STARTTLS nếu server hỗ trợ
                try:
                    server.starttls()
                except smtplib.SMTPNotSupportedError:
                    print("[reminder] Server không hỗ trợ STARTTLS, tiếp tục không TLS")
                except Exception as e:
                    print(f"[reminder] Lỗi STARTTLS: {e}, tiếp tục không TLS")
                
                server.login(SMTP_USER, SMTP_PASS)
                server.send_message(msg)

        print(f"[reminder] Đã gửi email tới {to_email}: {subject}")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"[reminder] Lỗi xác thực SMTP: {e}")
        print("[reminder] Kiểm tra username/password")
        return False
    except smtplib.SMTPException as e:
        print(f"[reminder] Lỗi SMTP: {e}")
        return False
    except Exception as e:
        print(f"[reminder] Lỗi kết nối: {e}")
        return False


def _get_pending_reminders(session: Session, window_start: datetime, window_end: datetime) -> List[Dict[str, Any]]:
    """
    Lấy danh sách event cần gửi reminder trong khoảng (window_start, window_end].
    Điều này tránh gửi reminder "sớm" nếu job quét với tần suất lớn hơn 1s,
    và đảm bảo reminder chỉ được gửi nếu reminder_time nằm trong cửa sổ quét gần nhất.
    """
    stmt = select(Event).where(Event.time_reminder != None, Event.reminder_sent_at == None)
    events = session.exec(stmt).all()

    pending: List[Dict[str, Any]] = []
    for ev in events:
        try:
            if not ev.start_time or ev.time_reminder is None:
                continue

            reminder_time = ev.start_time - timedelta(minutes=int(ev.time_reminder))

            # Chỉ chọn khi reminder_time nằm trong (window_start, window_end]
            if reminder_time > window_start and reminder_time <= window_end:
                user = session.get(User, ev.user_id)
                if not user or not getattr(user, "email", None):
                    continue

                pending.append({"event": ev, "user": user, "reminder_time": reminder_time})
        except Exception:
            continue

    return pending


def _mark_reminder_sent(session: Session, event: Event, sent_at: datetime):
    # Đánh dấu event đã gửi reminder
    try:
        event.reminder_sent_at = sent_at
        if hasattr(event, "reminder_sent"):
            event.reminder_sent = True
        session.add(event)
        session.commit()
    except Exception as exc:
        session.rollback()
        print(f"[reminder] Lỗi khi cập nhật trạng thái reminder cho event {getattr(event,'id',None)}: {exc}")


def _job_runner():
    # Job chính chạy định kỳ
    now = datetime.now()
    # Tính cửa sổ quét: (now - REMINDER_INTERVAL, now]
    window_start = now - timedelta(seconds=REMINDER_INTERVAL)
    window_end = now

    with Session(engine) as session:
        reminders = _get_pending_reminders(session, window_start, window_end)
        for item in reminders:
            ev = item["event"]
            user = item["user"]
            try:
                start_str = ev.start_time.strftime("%H:%M %d-%m-%Y") if ev.start_time else "Không rõ"
                subject = f"Nhắc: {ev.event_name}"
                body = (
                    f"Sự kiện '{ev.event_name}' sẽ bắt đầu lúc {start_str}.\n"
                    f"Địa điểm: {ev.location or 'Không rõ'}.\n"
                )

                sent = _send_email_smtp(user.email, subject, body)
                _mark_reminder_sent(session, ev, datetime.now())

                if sent:
                    print(f"[reminder] Đã gửi reminder cho event {ev.id} tới {user.email}")
                else:
                    print(f"[reminder] Gửi thất bại cho event {ev.id} tới {user.email}")
            except Exception as exc:
                print(f"[reminder] Gửi thất bại cho event {getattr(ev,'id',None)}: {exc}")


def start_scheduler(interval_seconds: Optional[int] = None):
    global _scheduler, REMINDER_INTERVAL
    if interval_seconds is None:
        interval_seconds = REMINDER_INTERVAL

    # Update global REMINDER_INTERVAL so runner uses correct window size
    REMINDER_INTERVAL = int(interval_seconds)

    if _scheduler is not None:
        return _scheduler

    _scheduler = BackgroundScheduler()
    _scheduler.add_job(_job_runner, "interval", seconds=interval_seconds, id="reminder_check")
    _scheduler.start()
    print(f"[reminder] Scheduler bắt đầu, kiểm tra mỗi {interval_seconds}s")
    return _scheduler


def stop_scheduler():
    global _scheduler
    if _scheduler:
        _scheduler.shutdown(wait=False)
        _scheduler = None
        print("[reminder] Scheduler dừng")


if __name__ == "__main__":
    start_scheduler(5)
    import time
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        stop_scheduler()