import re
from typing import Dict, Any, Optional, List

def extract_time(text: str) -> Dict[str, Any]:
    time_info = {
        'date_text': None,
        'time_start': None,
        'time_end': None,
        'raw_matches': [],
        'has_time_period': False,
        'time_period': None
    }

    m_period = re.search(r'\b(tối|sáng|chiều|trưa|đêm)\b', text, re.IGNORECASE)
    if m_period:
        time_info['has_time_period'] = True
        time_info['time_period'] = m_period.group(1).lower()

    date_patterns = [
        r'(\d{1,2}[/-]\d{1,2}(?:[/-]\d{2,4})?)',
        # Prefer matching weekday with week context first (e.g. "thứ bảy tuần sau")
        r'(thứ\s*(?:\d|hai|ba|tư|năm|sáu|bảy)(?:\s+tuần\s+(?:sau|này|tới))?)',
        r'(thứ\s*\d|thứ\s+(?:hai|ba|tư|năm|sáu|bảy)|t\d|chủ\s+nhật|cn)',
        r'(ngày\s+mai|hôm\s+nay|mai|ngày\s+kia|mốt)',
        r'(tuần\s+(?:sau|này|tới))',
    ]

    for pattern in date_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            time_info['date_text'] = match.group(1)
            time_info['raw_matches'].append(match.group(0))
            break

    if not time_info['date_text']:
        time_info['date_text'] = 'hôm nay'

    time_patterns = [
        (r'(\d{1,2}:\d{2})', lambda m: m.group(1)),
        (r'(\d{1,2})h(\d{0,2})(?!\s*trước)', lambda m: m.group(1) + 'h' + m.group(2)),
        (r'(\d{1,2})\s*giờ\s*(\d{0,2})(?!\s*trước)', lambda m: m.group(1) + 'giờ' + m.group(2)),
        (r'(\d{1,2})g(\d{0,2})', lambda m: m.group(1) + 'g' + m.group(2)),
        (r'lúc\s+(\d{1,2})\b(?!.*giờ)', lambda m: m.group(1) + ':00'),
    ]

    time_matches: List[str] = []
    for pattern, formatter in time_patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            time_str = formatter(match)
            time_matches.append(time_str)
            time_info['raw_matches'].append(match.group(0))

    if time_matches:
        time_info['time_start'] = time_matches[0]
        if len(time_matches) > 1:
            time_info['time_end'] = time_matches[1]

    from_to_match = re.search(r'từ\s+(.+?)\s+đến\s+(.+?)(?=\s|$)', text, re.IGNORECASE)
    if from_to_match:
        time_info['time_start'] = from_to_match.group(1).strip()
        time_info['time_end'] = from_to_match.group(2).strip()

    return time_info
