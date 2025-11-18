import re
from typing import Dict, Any, Optional, Tuple

from nlp.reminder import extract_reminder
from nlp.location import extract_location
from nlp.time_extractor import extract_time
from nlp.name_extractor import extract_event_name
from nlp.datetime_builder import build_datetime
from nlp.preprocess import normalize_text


class NLPProcessor:
    def process_text(self, text: str) -> Dict[str, Any]:
        try:
            original_text = text

            # preprocess (expand abbreviations, produce normalized & no-accent variants)
            pre = normalize_text(text)
            working = pre.get('normalized')
            # strip some punctuation for easier regex matching
            working = re.sub(r"[.,;!?\"']", '', working)

            minutes, text_no_reminder = extract_reminder(working)
            location, text_no_location = extract_location(text_no_reminder)
            time_info = extract_time(text_no_location)
            event_name = extract_event_name(text_no_location, time_info)

            start_dt, end_dt = build_datetime(time_info)

            result = {
                'event_name': event_name,
                'start_time': start_dt.strftime('%Y-%m-%d %H:%M:%S'),
                'end_time': end_dt.strftime('%Y-%m-%d %H:%M:%S') if end_dt else None,
                'location': location,
                'time_reminder': minutes,
                'success': True
            }

            return result

        except Exception as e:
            import traceback
            traceback.print_exc()
            return {'error': f'Không thể xử lý: {str(e)}', 'success': False}



