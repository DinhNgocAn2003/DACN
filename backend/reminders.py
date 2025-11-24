from datetime import datetime, timedelta
from typing import List, Dict, Any
import os
import smtplib
from email.message import EmailMessage
from sqlmodel import select
from sqlmodel import Session
from db import get_session, engine
from models.models import Event, User
from apscheduler.schedulers.background import BackgroundScheduler

# Configuration via environment variables
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
FROM_EMAIL = os.getenv("FROM_EMAIL", SMTP_USER or "noreply@example.com")

_scheduler: BackgroundScheduler = None


def _send_email_smtp(to_email: str, subject: str, body: str) -> None:
    """Send email via SMTP. If SMTP not configured, print to console."""
    if not SMTP_HOST or not SMTP_USER or not SMTP_PASS:
        print(f"[reminder] SMTP not configured - would send to {to_email}: {subject}\n{body}")
        return

    msg = EmailMessage()
    msg["From"] = FROM_EMAIL
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30) as s:
        try:
            s.starttls()
        except Exception:
            pass
        s.login(SMTP_USER, SMTP_PASS)
        s.send_message(msg)


def _get_pending_reminders(session: Session, before_dt: datetime) -> List[Dict[str, Any]]:
    results = []
    statement = select(Event).where(Event.reminder_sent == False, Event.time_reminder != None)
    events = session.exec(statement).all()
    for ev in events:
        try:
            if not ev.start_time or ev.time_reminder is None:
                continue
            reminder_time = ev.start_time - timedelta(minutes=int(ev.time_reminder))
            # if reminder_time has passed or is now, include
            if reminder_time <= before_dt:
                user = session.get(User, ev.user_id)
                if not user or not getattr(user, 'email', None):
                    continue
                results.append({
                    "event": ev,
                    "user": user,
                    "reminder_time": reminder_time,
                })
        except Exception:
            continue
    return results


def _mark_reminder_sent(session: Session, event_id: int, sent_at: datetime):
    ev = session.get(Event, event_id)
    if not ev:
        return
    ev.reminder_sent = True
    ev.reminder_sent_at = sent_at
    session.add(ev)
    session.commit()


def _job_runner():
def _job_runner():
    now = datetime.now()
    with Session(engine) as session:
        from datetime import datetime, timedelta
        from typing import List, Dict, Any
        import os
        import smtplib
        from email.message import EmailMessage
        from sqlmodel import select
        from sqlmodel import Session
        from db import get_session, engine
        from models.models import Event, User
        from apscheduler.schedulers.background import BackgroundScheduler

        # Cấu hình từ biến môi trường
        SMTP_HOST = os.getenv("SMTP_HOST")
        SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
        SMTP_USER = os.getenv("SMTP_USER")
        SMTP_PASS = os.getenv("SMTP_PASS")
        FROM_EMAIL = os.getenv("FROM_EMAIL", SMTP_USER or "noreply@example.com")
        # Khoảng thời gian (giây) để scheduler kiểm tra. Mặc định 60s.
        REMINDER_INTERVAL = int(os.getenv("REMINDER_INTERVAL", "60"))

        _scheduler: BackgroundScheduler = None


        def _send_email_smtp(to_email: str, subject: str, body: str) -> None:
            """Gửi email qua SMTP. Nếu chưa cấu hình SMTP, in log thay vì gửi."""
            if not SMTP_HOST or not SMTP_USER or not SMTP_PASS:
                print(f"[reminder] SMTP chưa cấu hình - sẽ gửi tới {to_email}: {subject}\n{body}")
                return

            msg = EmailMessage()
            msg["From"] = FROM_EMAIL
            msg["To"] = to_email
            msg["Subject"] = subject
            msg.set_content(body)

            with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30) as s:
                try:
                    s.starttls()
                except Exception:
                    pass
                s.login(SMTP_USER, SMTP_PASS)
                s.send_message(msg)


        def _get_pending_reminders(session: Session, before_dt: datetime) -> List[Dict[str, Any]]:
            """Trả về danh sách reminders cần gửi: reminder chưa gửi và reminder_time <= before_dt.

            Thuật toán: reminder_time = event.start_time - minutes(event.time_reminder)
            """
            results = []
            statement = select(Event).where(Event.reminder_sent == False, Event.time_reminder != None)
            events = session.exec(statement).all()
            for ev in events:
                try:
                    if not ev.start_time or ev.time_reminder is None:
                        continue
                    reminder_time = ev.start_time - timedelta(minutes=int(ev.time_reminder))
                    # nếu đã đến hoặc vượt thời điểm reminder thì đưa vào danh sách
                    if reminder_time <= before_dt:
                        user = session.get(User, ev.user_id)
                        if not user or not getattr(user, 'email', None):
                            continue
                        results.append({
                            "event": ev,
                            "user": user,
                            "reminder_time": reminder_time,
                        })
                except Exception:
                    continue
            return results


        def _mark_reminder_sent(session: Session, event_id: int, sent_at: datetime):
            ev = session.get(Event, event_id)
            if not ev:
                return
            ev.reminder_sent = True
            ev.reminder_sent_at = sent_at
            session.add(ev)
            session.commit()


        def _job_runner():
            now = datetime.now()
            with Session(engine) as session:
                from datetime import datetime, timedelta
                from typing import List, Dict, Any
                import os
                import smtplib
                from email.message import EmailMessage
                from sqlmodel import select
                from sqlmodel import Session
                from db import engine
                from models.models import Event, User
                from apscheduler.schedulers.background import BackgroundScheduler

                # Cấu hình từ biến môi trường
                SMTP_HOST = os.getenv("SMTP_HOST")
                SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
                SMTP_USER = os.getenv("SMTP_USER")
                SMTP_PASS = os.getenv("SMTP_PASS")
                FROM_EMAIL = os.getenv("FROM_EMAIL", SMTP_USER or "noreply@example.com")
                # Khoảng thời gian (giây) để scheduler kiểm tra. Mặc định 60s.
                REMINDER_INTERVAL = int(os.getenv("REMINDER_INTERVAL", "60"))

                # Biến scheduler toàn cục
                _scheduler: BackgroundScheduler = None


                # Gửi email qua SMTP. Nếu chưa cấu hình SMTP, in log để dev biết.
                def _send_email_smtp(to_email: str, subject: str, body: str) -> None:
                    """Gửi email qua SMTP. Nếu chưa cấu hình SMTP, in log thay vì gửi thực tế."""
                    if not SMTP_HOST or not SMTP_USER or not SMTP_PASS:
                        # Thông báo cho console thay vì ném lỗi — hữu ích khi chạy local
                        print(f"[reminder] SMTP chưa cấu hình - sẽ gửi tới {to_email}: {subject}\n{body}")
                        return

                    msg = EmailMessage()
                    msg["From"] = FROM_EMAIL
                    msg["To"] = to_email
                    msg["Subject"] = subject
                    msg.set_content(body)

                    # Kết nối tới server SMTP, bật TLS nếu được hỗ trợ
                    with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30) as s:
                        try:
                            s.starttls()
                        except Exception:
                            # Nếu server không hỗ trợ STARTTLS, bỏ qua
                            pass
                        s.login(SMTP_USER, SMTP_PASS)
                        s.send_message(msg)


                # Lấy danh sách event cần gửi reminder (chưa gửi và có time_reminder)
                def _get_pending_reminders(session: Session, before_dt: datetime) -> List[Dict[str, Any]]:
                    """Trả về danh sách reminders cần gửi: reminder chưa gửi và reminder_time <= before_dt.

                    Thuật toán: reminder_time = event.start_time - minutes(event.time_reminder)
                    """
                    results: List[Dict[str, Any]] = []

                    # Lọc những event chưa gửi reminder và có trường time_reminder
                    statement = select(Event).where(Event.reminder_sent == False, Event.time_reminder != None)
                    events = session.exec(statement).all()

                    for ev in events:
                        try:
                            # Bỏ qua event không có start_time hoặc không có time_reminder
                            if not ev.start_time or ev.time_reminder is None:
                                continue

                            # Tính thời điểm cần gửi reminder
                            reminder_time = ev.start_time - timedelta(minutes=int(ev.time_reminder))

                            # Nếu đã tới hoặc vượt thời điểm reminder, đưa vào danh sách
                            if reminder_time <= before_dt:
                                user = session.get(User, ev.user_id)
                                # Nếu không có user hoặc user không có email thì bỏ qua
                                if not user or not getattr(user, 'email', None):
                                    continue

                                results.append({
                                    "event": ev,
                                    "user": user,
                                    "reminder_time": reminder_time,
                                })
                        except Exception:
                            # Nếu có lỗi với một event nào đó, bỏ qua để không ảnh hưởng cả vòng
                            continue

                    return results


                # Đánh dấu event đã gửi reminder thành công
                def _mark_reminder_sent(session: Session, event_id: int, sent_at: datetime):
                    ev = session.get(Event, event_id)
                    if not ev:
                        return
                    ev.reminder_sent = True
                    ev.reminder_sent_at = sent_at
                    session.add(ev)
                    session.commit()


                # Job chính: chạy định kỳ, tìm các reminder cần gửi và gửi email
                def _job_runner():
                    now = datetime.now()
                    # Mở session DB, chỉ dùng trong phạm vi job này
                    with Session(engine) as session:
                        reminders = _get_pending_reminders(session, now)
                        for r in reminders:
                            ev = r['event']
                            user = r['user']
                            try:
                                # Tạo nội dung email cơ bản
                                subject = f"Nhắc: {ev.event_name}"
                                start_str = ev.start_time.strftime('%Y-%m-%d %H:%M') if ev.start_time else 'Không rõ'
                                body = (
                                    f"Sự kiện '{ev.event_name}' sẽ bắt đầu lúc {start_str}.\\n"
                                    f"Địa điểm: {ev.location or 'Không rõ'}."
                                )

                                # Gửi email (hoặc log nếu SMTP chưa cấu hình)
                                _send_email_smtp(user.email, subject, body)

                                # Nếu gửi thành công (hoặc đã log), đánh dấu đã gửi để tránh lặp
                                _mark_reminder_sent(session, ev.id, datetime.now())

                                print(f"[reminder] Đã gửi reminder cho event {ev.id} tới {user.email}")
                            except Exception as e:
                                # Ghi log lỗi để dễ debug
                                print(f"[reminder] Gửi thất bại cho event {ev.id}: {e}")


                # Bắt đầu scheduler (gọi từ main startup)
                def start_scheduler(interval_seconds: int = None):
                    global _scheduler
                    if interval_seconds is None:
                        interval_seconds = REMINDER_INTERVAL
                    if _scheduler is not None:
                        return _scheduler

                    # Tạo scheduler nền và đăng ký job
                    _scheduler = BackgroundScheduler()
                    _scheduler.add_job(_job_runner, 'interval', seconds=interval_seconds, id='reminder_check')
                    _scheduler.start()

                    print(f"[reminder] Scheduler bắt đầu, khoảng kiểm tra = {interval_seconds}s")
                    return _scheduler
                # Dừng scheduler (gọi từ main shutdown)
                def stop_scheduler():
                    global _scheduler
                    if _scheduler:
                        _scheduler.shutdown(wait=False)
                        _scheduler = None
                        print("[reminder] Scheduler dừng")