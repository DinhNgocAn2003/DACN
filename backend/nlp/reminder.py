import re
from typing import Tuple, Optional

def extract_reminder(text: str) -> Tuple[Optional[int], str]:
    #Trích xuất thông tin nhắc nhở (phút) và trả về (minutes, cleaned_text).
    patterns = [
        r'(?:nhắc|báo)\s*(?:tôi|tui|mình|em|anh|chị)?\s+trước\s+(\d+)\s*(?:tiếng|giờ)',
        r'(?:nhắc|báo)\s*(?:tôi|tui|mình|em|anh|chị)?\s+(\d+)\s*(?:tiếng|giờ)\s+trước',
        r'trước\s+(\d+)\s*(?:tiếng|giờ)',
        r'(\d+)\s*(?:tiếng|giờ)\s+trước',
        r'(?:nhắc|báo)\s*(?:tôi|tui|mình|em|anh|chị)?\s+trước\s+(\d+)\s*phút',
        r'(?:nhắc|báo)\s*(?:tôi|tui|mình|em|anh|chị)?\s+(\d+)\s*phút\s+trước',
        r'trước\s+(\d+)\s*phút',
        r'(\d+)\s*phút\s+trước',
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            minutes = int(match.group(1))
            matched_text = match.group(0).lower()
            if 'giờ' in matched_text or 'tiếng' in matched_text:
                minutes *= 60
            text_clean = text[:match.start()] + text[match.end():]
            return minutes, text_clean.strip()

    # Nếu chỉ có từ khóa 'nhắc' hoặc 'báo' mà không có số phút cụ thể thì
    # trả về (None, cleaned_text) để frontend/backends khác có thể quyết định.
    if re.search(r'\b(nhắc|báo)\b', text, re.IGNORECASE):
        text_clean = re.sub(r'^\s*(?:nhắc|báo)\s+(?:tôi|tui|em|mình|anh|chị)\s+', '', text, flags=re.IGNORECASE)
        return None, text_clean

    # Không tìm thấy thông tin nhắc -> không đặt mặc định
    return None, text
