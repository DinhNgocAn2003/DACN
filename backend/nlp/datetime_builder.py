import re
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple


def parse_time_string(time_str: Optional[str]) -> Tuple[Optional[int], Optional[int]]:
    if not time_str:
        return None, None
    s = time_str.strip().lower()
    m = re.match(r'(\d{1,2}):(\d{2})', s)
    if m:
        return int(m.group(1)), int(m.group(2))
    m = re.match(r'(\d{1,2})h(\d{0,2})', s)
    if m:
        hour = int(m.group(1))
        minute = int(m.group(2)) if m.group(2) else 0
        return hour, minute
    m = re.match(r'(\d{1,2})\s*giờ\s*(\d{0,2})', s)
    if m:
        hour = int(m.group(1))
        minute = int(m.group(2)) if m.group(2) else 0
        return hour, minute
    m = re.match(r'(\d{1,2})g(\d{0,2})', s)
    if m:
        hour = int(m.group(1))
        minute = int(m.group(2)) if m.group(2) else 0
        return hour, minute
    m = re.match(r'(\d{1,2})', s)
    if m:
        return int(m.group(1)), 0
    return None, None


def build_datetime(time_info: Dict) -> Tuple[datetime, Optional[datetime]]:
    now = datetime.now()
    date_text = time_info.get('date_text', 'hôm nay').lower()
    base_date = now.date()

    if date_text in ['hôm nay', 'bữa nay']:
        base_date = now.date()
    elif date_text in ['mai', 'ngày mai']:
        base_date = (now + timedelta(days=1)).date()
    elif date_text in ['ngày kia', 'mốt']:
        base_date = (now + timedelta(days=2)).date()
    elif 'thứ' in date_text or date_text in ['t2', 't3', 't4', 't5', 't6', 't7', 'cn']:
        day_map = {
            'thứ 2': 0, 'thứ hai': 0, 't2': 0,
            'thứ 3': 1, 'thứ ba': 1, 't3': 1,
            'thứ 4': 2, 'thứ tư': 2, 't4': 2,
            'thứ 5': 3, 'thứ năm': 3, 't5': 3,
            'thứ 6': 4, 'thứ sáu': 4, 't6': 4,
            'thứ 7': 5, 'thứ bảy': 5, 't7': 5,
            'chủ nhật': 6, 'cn': 6,
        }
        target_day = None
        for key, day_num in day_map.items():
            if key in date_text.lower():
                target_day = day_num
                break
        if target_day is not None:
            current_day = now.weekday()
            days_ahead = (target_day - current_day) % 7
            if days_ahead == 0:
                days_ahead = 7
            # If the phrase included a week modifier like "tuần sau/tới",
            # interpret it as the same weekday in the next week. Only add
            # an extra 7 days when the computed next occurrence is within
            # the current week (days_ahead < 7). This avoids doubling the
            # offset when the next occurrence already points to next week.
            if 'tuần' in date_text and ('sau' in date_text or 'tới' in date_text):
                if days_ahead < 7:
                    days_ahead += 7

            base_date = (now + timedelta(days=days_ahead)).date()
    elif re.match(r'\d{1,2}[/-]\d{1,2}', date_text):
        try:
            parts = re.split(r'[/-]', date_text)
            day = int(parts[0])
            month = int(parts[1])
            year = now.year
            if len(parts) == 3:
                year = int(parts[2])
                if year < 100:
                    year += 2000
            base_date = datetime(year, month, day).date()
            if base_date < now.date():
                base_date = datetime(year + 1, month, day).date()
        except:
            base_date = now.date()

    time_start = time_info.get('time_start')
    time_end = time_info.get('time_end')

    hour_start, minute_start = parse_time_string(time_start)
    # If a time period (sáng/chiều/tối/trưa/đêm) was detected, adjust
    # hour into 24-hour clock when an explicit hour was provided.
    time_period = time_info.get('time_period')
    if hour_start is not None and time_period:
        tp = time_period.lower()
        # normalize some variants
        if tp in ('chiều', 'tối', 'đêm'):
            if hour_start < 12:
                hour_start = (hour_start % 12) + 12
        elif tp == 'sáng':
            # '12 giờ sáng' -> 0
            if hour_start == 12:
                hour_start = 0
        elif tp == 'trưa':
            # treat 'trưa' as midday; if user wrote a single hour like '1 trưa'
            # keep it as is unless it's ambiguous; we won't shift by default
            if hour_start == 12:
                hour_start = 12
    if hour_start is None:
        if time_info.get('has_time_period'):
            hour_start, minute_start = 19, 0
        else:
            hour_start, minute_start = 9, 0

    start_datetime = datetime.combine(base_date, datetime.min.time()).replace(
        hour=hour_start, minute=minute_start, second=0, microsecond=0
    )

    now = datetime.now()
    if start_datetime < now and start_datetime.date() == now.date():
        start_datetime += timedelta(days=1)

    end_datetime = None
    if time_end:
        hour_end, minute_end = parse_time_string(time_end)
        if hour_end is not None:
            end_datetime = datetime.combine(base_date, datetime.min.time()).replace(
                hour=hour_end, minute=minute_end, second=0, microsecond=0
            )
            if end_datetime <= start_datetime:
                end_datetime += timedelta(days=1)
            if end_datetime < now:
                end_datetime += timedelta(days=1)

    return start_datetime, end_datetime
