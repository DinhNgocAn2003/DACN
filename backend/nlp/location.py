import re
from typing import Tuple, Optional

def extract_location(text: str) -> Tuple[Optional[str], str]:
    # Dừng trích xuất location trước các từ khóa thời gian hoặc dấu kết thúc
    time_lookahead = r"(?:lúc|vào|từ|đến|nhắc|báo|ngày|mai|hôm|mốt|chiều|tối|trưa|sáng|\d{1,2}[:h]|giờ|g)"
    patterns = [
        rf'(?:tại|ở|chỗ|nơi)\s+([^,\.\n!?]+?)(?=\s*$|\s+{time_lookahead})',
        rf'(?:tại|ở|chỗ|nơi)\s+(.+?)(?=\s*$|\s+{time_lookahead})'
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            location = match.group(1).strip()
            text_clean = text[:match.start()] + text[match.end():]
            return location, text_clean.strip()

    return None, text
