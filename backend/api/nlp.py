from fastapi import APIRouter, HTTPException
from nlp_processor import NLPProcessor
from models.schemas import TextRequest

router = APIRouter()
processor = NLPProcessor()

# Endpoint NLP: parse text and extract event fields

@router.post("/parse")
async def parse_text(request: TextRequest):
    """
    Nhận text tiếng Việt và trả về JSON với các field:
    event_name, start_time, end_time, location, time_reminder
    """
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Missing text")
    
    try:
        result = processor.process_text(request.text)
        
        # Trả về chỉ các field cần thiết
        response = {
            "event_name": result.get("event_name"),
            "start_time": result.get("start_time"),
            "end_time": result.get("end_time"),
            "location": result.get("location"),
            "time_reminder": result.get("time_reminder")
        }
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing text: {str(e)}")