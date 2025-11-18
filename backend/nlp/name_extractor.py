import re
from typing import Dict

def extract_event_name(text: str, time_info: Dict) -> str:
    cleaned = text

    for raw_match in time_info.get('raw_matches', []):
        cleaned = cleaned.replace(raw_match, '')

    # Remove time-related keywords; include common non-diacritic variants so inputs
    # like 'nay' (without accent) are also handled.
    time_keywords = [
        r'\b(?:vào|lúc|từ|đến|ngày|thời gian|khoảng|này|nay|kia)\b',
        r'\b(?:sáng|sang|chiều|chieu|tối|toi|trưa|trua|đêm|dem)\b',
        r'\b(?:hôm|hom)\b',
        r'\b(?:hôm nay|hom nay|ngày mai|ngay mai|mai)\b'
    ]
    for keyword in time_keywords:
        cleaned = re.sub(keyword, '', cleaned, flags=re.IGNORECASE)

    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    cleaned = cleaned.strip('.,!?;: ')

    if cleaned:
        cleaned = cleaned[0].upper() + cleaned[1:]

    return cleaned if cleaned else 'Sự kiện mới'
