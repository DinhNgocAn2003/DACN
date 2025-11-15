import re
from typing import Dict

def extract_event_name(text: str, time_info: Dict) -> str:
    cleaned = text

    for raw_match in time_info.get('raw_matches', []):
        cleaned = cleaned.replace(raw_match, '')

    time_keywords = [
        r'\b(?:vào|lúc|từ|đến|ngày|thời gian|khoảng|này|kia)\b',
        r'\b(?:sáng|chiều|tối|trưa|đêm)\b',
    ]
    for keyword in time_keywords:
        cleaned = re.sub(keyword, '', cleaned, flags=re.IGNORECASE)

    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    cleaned = cleaned.strip('.,!?;: ')

    if cleaned:
        cleaned = cleaned[0].upper() + cleaned[1:]

    return cleaned if cleaned else 'Sự kiện mới'
