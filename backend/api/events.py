from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from db import get_session
from models.schemas import EventCreate
import logging

logger = logging.getLogger(__name__)

try:
    from models import Event, User
except ImportError:
    # Dùng package models; nếu lỗi import, kiểm tra PYTHONPATH
    from models import Event, User

router = APIRouter()
# Endpoints quản lý sự kiện: liệt kê, tạo, lấy, cập nhật, xóa

@router.get("", response_model=dict)
# Lấy danh sách tất cả sự kiện
async def list_events(session: Session = Depends(get_session)):
    try:
        logger.info("GET /events endpoint called")
        events = session.exec(select(Event)).all()
        result = {"events": [event.dict() for event in events], "count": len(events)}
        logger.info(f"Found {len(events)} events")
        return result
    except Exception as e:
        logger.error(f"Error fetching events: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching events: {str(e)}")

@router.post("", response_model=dict)
# Tạo sự kiện mới
async def create_event(event: EventCreate, session: Session = Depends(get_session)):
    try:
        # Kiểm tra user_id có tồn tại không
        user = session.get(User, event.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        e = Event(**event.dict())
        session.add(e)
        session.commit()
        session.refresh(e)

        return e.dict()

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating event: {str(e)}")

@router.get("/user/{user_id}", response_model=dict)
# Lấy các sự kiện theo user id
async def list_events_by_user(user_id: int, session: Session = Depends(get_session)):
    try:
        user = session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        events = session.exec(select(Event).where(Event.user_id == user_id)).all()
        return {"events": [event.dict() for event in events], "count": len(events)}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching user events: {str(e)}")

@router.get("/{event_id}", response_model=dict)
# Lấy chi tiết một sự kiện theo id
async def get_event(event_id: int, session: Session = Depends(get_session)):
    try:
        event = session.get(Event, event_id)
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        return event.dict()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching event: {str(e)}")

@router.put("/{event_id}", response_model=dict)
# Cập nhật sự kiện theo id
async def update_event(event_id: int, event: EventCreate, session: Session = Depends(get_session)):
    try:
        existing = session.get(Event, event_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Event not found")

        # Kiểm tra user tồn tại
        user = session.get(User, event.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Cập nhật các trường
        existing.user_id = event.user_id
        existing.event_name = event.event_name
        existing.start_time = event.start_time
        existing.end_time = event.end_time
        existing.location = event.location
        existing.time_reminder = event.time_reminder

        session.add(existing)
        session.commit()
        session.refresh(existing)

        return existing.dict()

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating event: {str(e)}")

@router.delete("/{event_id}", response_model=dict)
# Xóa sự kiện theo id
async def delete_event(event_id: int, session: Session = Depends(get_session)):
    """Delete an event by id"""
    try:
        existing = session.get(Event, event_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Event not found")

        session.delete(existing)
        session.commit()

        return {"ok": True, "message": "Event deleted"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting event: {str(e)}")