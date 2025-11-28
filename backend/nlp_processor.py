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

            # Tiền xử lý: tạo bản chuẩn hóa (lower/no-accent) và bản raw
            pre = normalize_text(text)
            working_norm = pre.get('normalized')
            # Loại bỏ một số dấu câu để regex hoạt động dễ dàng hơn
            working_norm = re.sub(r"[.,;!?\"']", '', working_norm)

            # Trích xuất location từ bản raw (giữ nguyên chữ hoa/chữ thường)
            raw_for_location = re.sub(r"[.,;!?\"']", '', pre.get('raw'))
            location, _ = extract_location(raw_for_location)
            # Nếu tìm thấy location, loại bỏ cụm đó khỏi bản normalized để tránh ảnh hưởng tới trích xuất thời gian
            if location:
                # Khi loại location khỏi bản normalized, xóa luôn tiền tố như 'tại', 'ở', 'chỗ', 'nơi'
                # để tránh còn lại từ như 'tại' trong event_name.
                try:
                    prefix_pattern = r"(?:\b(?:tại|ở|chỗ|nơi)\b\s*)?"
                    pattern = rf"{prefix_pattern}{re.escape(location.lower())}"
                    working_norm = re.sub(pattern, '', working_norm, flags=re.IGNORECASE)
                except Exception:
                    # Fallback: xóa location và sau đó loại tiền tố chung nếu còn
                    working_norm = working_norm.replace(location.lower(), '')
                    working_norm = re.sub(r"(?:\b(?:tại|ở|chỗ|nơi)\b\s*)", '', working_norm, flags=re.IGNORECASE)
                working_norm = re.sub(r"\s+", ' ', working_norm).strip()

            # Trích xuất reminder và phần còn lại dựa trên bản normalized
            minutes, text_no_reminder = extract_reminder(working_norm)
            time_info = extract_time(text_no_reminder)
            event_name = extract_event_name(text_no_reminder, time_info)

            # Xây dựng datetime — nếu có ngày không hợp lệ, build_datetime sẽ ném ValueError và ta báo về người dùng
            try:
                start_dt, end_dt = build_datetime(time_info)
            except ValueError as e:
                return {'error': str(e), 'success': False}

            # Tập hợp kết quả trả về dưới dạng dict chuẩn
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



