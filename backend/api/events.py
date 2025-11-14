from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from db import get_session
from models.schemas import EventCreate
import logging

logger = logging.getLogger(__name__)

try:
    from models import Event, User
except ImportError:
    # Fallback removed — rely on the package `models` (re-exports in models/__init__.py)
    # If you run into import issues, ensure the `backend` directory is on PYTHONPATH
    from models import Event, User

router = APIRouter()

@router.get("", response_model=dict)
async def list_events(session: Session = Depends(get_session)):
    """Get all events - DEBUG ENDPOINT"""
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
async def create_event(event: EventCreate, session: Session = Depends(get_session)):
    """Create a new event"""
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
async def list_events_by_user(user_id: int, session: Session = Depends(get_session)):
    """Get events by user ID"""
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
async def get_event(event_id: int, session: Session = Depends(get_session)):
    """Get a specific event by ID"""
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
async def update_event(event_id: int, event: EventCreate, session: Session = Depends(get_session)):
    """Update an event"""
    try:
        existing = session.get(Event, event_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Event not found")

        # Ensure the target user exists
        user = session.get(User, event.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Update fields
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