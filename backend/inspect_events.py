# inspect_events.py
# Run from repository root: python backend\inspect_events.py
from sqlmodel import Session, select
import os, sys
BASE_DIR = os.path.dirname(__file__)
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from db import engine
from models import Event

with Session(engine) as session:
    events = session.exec(select(Event)).all()
    print('Found', len(events), 'events')
    for e in events:
        print('Event id=', e.id)
        for field in ['start_time','end_time','created_at']:
            val = getattr(e, field)
            print(f'  {field}:', type(val), repr(val))
        try:
            d = e.dict()
            print(' e.dict() ok')
        except Exception as ex:
            print(' e.dict() -> Exception:', ex)
            raise
