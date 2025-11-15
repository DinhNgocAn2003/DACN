import re
from typing import Tuple, Optional

def extract_location(text: str) -> Tuple[Optional[str], str]:
    patterns = [
        r'(?:tại|ở|chỗ|nơi)\s+([^,\.\n!?]+?)(?=\s*$|\s+(?:lúc|vào|từ|đến|nhắc|báo))',
        r'(?:tại|ở|chỗ|nơi)\s+(.+?)(?=\s*$)'
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            location = match.group(1).strip()
            text_clean = text[:match.start()] + text[match.end():]
            return location, text_clean.strip()

    return None, text
