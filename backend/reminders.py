import os
import smtplib
from email.message import EmailMessage
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from apscheduler.schedulers.background import BackgroundScheduler
from sqlmodel import Session, select

# Import engine và models từ module nội bộ
from db import engine
from models import Event, User


# ======= CẤU HÌNH SMTP =======
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
FROM_EMAIL = os.getenv("FROM_EMAIL") or SMTP_USER

# Khoảng thời gian (giây) để job kiểm tra reminder
REMINDER_INTERVAL = int(os.getenv("REMINDER_INTERVAL", "60"))


_scheduler: Optional[BackgroundScheduler] = None


def _send_email_smtp(to_email: str, subject: str, body: str) -> None:
    """Gửi email bằng SMTP; nếu không có cấu hình thì ghi log thay vì gửi.

    Hàm này tránh ném lỗi để scheduler không bị dừng vì vấn đề transport.
    """
    if not SMTP_HOST or not SMTP_USER or not SMTP_PASS:
        print(f"[reminder] SMTP chưa cấu hình. Thay vì gửi, in log cho {to_email}: {subject}")
        print(body)
        return

    msg = EmailMessage()
    msg["From"] = FROM_EMAIL
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30) as s:
            try:
                s.starttls()
            except Exception:
                pass
            s.login(SMTP_USER, SMTP_PASS)
            s.send_message(msg)
    except Exception as exc:
        print(f"[reminder] Lỗi SMTP khi gửi tới {to_email}: {exc}")


def _get_pending_reminders(session: Session, before_dt: datetime) -> List[Dict[str, Any]]:
    """Lấy danh sách event cần gửi reminder trước `before_dt`.

    Tiêu chí:
    - `time_reminder` không phải None (số phút trước start_time)
    - `reminder_sent_at` là NULL (chưa gửi)
    """
    stmt = select(Event).where(Event.time_reminder != None, Event.reminder_sent_at == None)
    events = session.exec(stmt).all()

    pending: List[Dict[str, Any]] = []
    for ev in events:
        try:
            if not ev.start_time or ev.time_reminder is None:
                continue

            reminder_time = ev.start_time - timedelta(minutes=int(ev.time_reminder))
            if reminder_time <= before_dt:
                user = session.get(User, ev.user_id)
                if not user or not getattr(user, "email", None):
                    continue

                pending.append({"event": ev, "user": user, "reminder_time": reminder_time})
        except Exception:
            # bỏ qua event nếu có dữ liệu sai
            continue

    return pending


def _mark_reminder_sent(session: Session, event: Event, sent_at: datetime):
    """Đánh dấu event đã gửi reminder: đặt `reminder_sent_at` và nếu có `reminder_sent` thì cũng đặt True."""
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
    """Job chính chạy định kỳ: lấy danh sách pending và gửi email."""
    now = datetime.utcnow()
    with Session(engine) as session:
        reminders = _get_pending_reminders(session, now)
        for item in reminders:
            ev = item["event"]
            user = item["user"]
            try:
                start_str = ev.start_time.strftime("%Y-%m-%d %H:%M") if ev.start_time else "Không rõ"
                subject = f"Nhắc: {ev.event_name}"
                body = (
                    f"Sự kiện '{ev.event_name}' sẽ bắt đầu lúc {start_str}.\n"
                    f"Địa điểm: {ev.location or 'Không rõ'}.\n"
                )

                _send_email_smtp(user.email, subject, body)

                _mark_reminder_sent(session, ev, datetime.utcnow())

                print(f"[reminder] Đã gửi reminder cho event {ev.id} tới {user.email}")
            except Exception as exc:
                print(f"[reminder] Gửi thất bại cho event {getattr(ev,'id',None)}: {exc}")


def start_scheduler(interval_seconds: Optional[int] = None):
    global _scheduler
    if interval_seconds is None:
        interval_seconds = REMINDER_INTERVAL

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
    # Đoạn chạy nhanh để test manual
    start_scheduler(5)
    import time
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        stop_scheduler()
