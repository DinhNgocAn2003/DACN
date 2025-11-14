import re
import dateparser
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any

class NLPProcessor:
    def __init__(self):
        self.time_keywords = ['lúc', 'vào', 'từ', 'đến', 'thời gian', 'ngày', 'khoảng']
        self.location_keywords = ['tại', 'ở', 'địa điểm', 'chỗ', 'nơi', 'phòng']
        self.reminder_keywords = ['nhắc', 'nhắc nhở', 'báo', 'nhắc trước', 'báo trước']
        
        # Từ điển thời gian tiếng Việt
        self.time_mapping = {
            # Ngày
            'hôm nay': 'today', 'hôm qua': 'yesterday', 'mai': 'tomorrow', 
            'ngày mai': 'tomorrow', 'ngày kia': 'in 2 days', 'mốt': 'in 2 days',
            
            # Tuần
            'tuần này': 'this week', 'tuần sau': 'next week', 'tuần tới': 'next week',
            
            # Thứ trong tuần
            'thứ hai': 'monday', 'thứ ba': 'tuesday', 'thứ tư': 'wednesday',
            'thứ năm': 'thursday', 'thứ sáu': 'friday', 'thứ bảy': 'saturday',
            'chủ nhật': 'sunday', 'cn': 'sunday',
            'thứ 2': 'monday', 'thứ 3': 'tuesday', 'thứ 4': 'wednesday',
            'thứ 5': 'thursday', 'thứ 6': 'friday', 'thứ 7': 'saturday',
            't2': 'monday', 't3': 'tuesday', 't4': 'wednesday',
            't5': 'thursday', 't6': 'friday', 't7': 'saturday',
            
            # Buổi trong ngày
            'sáng': 'morning', 'chiều': 'afternoon', 'tối': 'evening',
            'đêm': 'night', 'trưa': 'noon',
            'sáng nay': 'this morning', 'chiều nay': 'this afternoon', 
            'tối nay': 'this evening', 'trưa nay': 'this noon',
            'sáng mai': 'tomorrow morning', 'chiều mai': 'tomorrow afternoon',
            'tối mai': 'tomorrow evening',
        }
    
    def process_text(self, text: str) -> Dict[str, Any]:
        """
        Xử lý văn bản và trích xuất thông tin sự kiện
        Chiến lược: Tách từng phần một cách rõ ràng
        """
        try:
            # print(f"\n{'='*60}")
            # print(f"Đang xử lý: {text}")
            # print(f"{'='*60}")
            
            original_text = text
            text = re.sub(r'[.,:;!?]', '', text)  # Loại bỏ dấu câu để dễ xử lýs
            # Bước 1: Trích xuất REMINDER trước (vì có từ "nhắc" có thể gây nhầm lẫn)
            time_reminder, text_without_reminder = self._extract_reminder_advanced(text)
            # print(f"📢 Reminder: {time_reminder} phút")
            # print(f"Văn bản sau khi bỏ reminder: '{text_without_reminder}'")
            
            # Bước 2: Trích xuất LOCATION
            location, text_without_location = self._extract_location_advanced(text_without_reminder)
            # print(f"📍 Location: '{location}'")
            # print(f"Văn bản sau khi bỏ location: '{text_without_location}'")
            
            # Bước 3: Trích xuất THỜI GIAN (start và end)
            time_info = self._extract_time_advanced(text_without_location)
            # print(f"⏰ Time info: {time_info}")
            
            # Bước 4: Trích xuất TÊN SỰ KIỆN (phần còn lại)
            event_name = self._extract_event_name_advanced(
                text_without_location, 
                time_info
            )
            # print(f"📝 Event name: '{event_name}'")
            
            # Bước 5: Xây dựng datetime chính xác
            start_time, end_time = self._build_datetime(time_info)
            # print(f"🕐 Start: {start_time}")
            # print(f"🕐 End: {end_time}")
            
            result = {
                'event_name': event_name,
                'start_time': start_time.strftime('%Y-%m-%d %H:%M:%S'),
                'end_time': end_time.strftime('%Y-%m-%d %H:%M:%S') if end_time else None,
                'location': location,
                'time_reminder': time_reminder,
                'success': True
            }
            
            # print(f"\n✅ Kết quả cuối cùng:")
            # print(f"   Event: {event_name}")
            # print(f"   Start: {start_time.strftime('%d/%m/%Y %H:%M')}")
            # print(f"   End: {end_time.strftime('%d/%m/%Y %H:%M') if end_time else 'None'}")
            # print(f"   Location: {location}")
            # print(f"   Reminder: {time_reminder} phút")
            # print(f"{'='*60}\n")
            
            return result
            
        except Exception as e:
            print(f"❌ Lỗi: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                'error': f'Không thể xử lý: {str(e)}',
                'success': False
            }
    
    def _extract_reminder_advanced(self, text: str) -> Tuple[int, str]:
        """Trích xuất thông tin nhắc nhở và loại bỏ khỏi text"""
        patterns = [
        # "nhắc tôi trước 10 tiếng", "báo tui trước 2 giờ"
        r'(?:nhắc|báo)\s*(?:tôi|tui|mình|em|anh|chị)?\s+trước\s+(\d+)\s*(?:tiếng|giờ)',
        # "nhắc tui 10 tiếng trước", "báo tôi 2 giờ trước"
        r'(?:nhắc|báo)\s*(?:tôi|tui|mình|em|anh|chị)?\s+(\d+)\s*(?:tiếng|giờ)\s+trước',
        # "trước 10 tiếng", "trước 2 giờ"  (không cần "tôi" ở đây)
        r'trước\s+(\d+)\s*(?:tiếng|giờ)',
        r'(\d+)\s*(?:tiếng|giờ)\s+trước',
        # "nhắc trước 15 phút", "báo trước 30 phút" với "tôi", "tui"
        r'(?:nhắc|báo)\s*(?:tôi|tui|mình|em|anh|chị)?\s+trước\s+(\d+)\s*phút',
        r'(?:nhắc|báo)\s*(?:tôi|tui|mình|em|anh|chị)?\s+(\d+)\s*phút\s+trước',
        r'trước\s+(\d+)\s*phút',
        r'(\d+)\s*phút\s+trước',
    ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                minutes = int(match.group(1))
                # Nếu là giờ hoặc tiếng, chuyển sang phút
                matched_text = match.group(0).lower()
                if 'giờ' in matched_text or 'tiếng' in matched_text:
                    minutes *= 60
                # Loại bỏ phần reminder khỏi text
                text_clean = text[:match.start()] + text[match.end():]
                return minutes, text_clean.strip()
        
        # Kiểm tra nếu chỉ có từ "nhắc" mà không có số
        if re.search(r'\b(nhắc|báo)\b', text, re.IGNORECASE):
            # Loại bỏ từ "nhắc tôi", "nhắc em" ở đầu
            text_clean = re.sub(r'^\s*(?:nhắc|báo)\s+(?:tôi|tui|em|mình|anh|chị)\s+', '', text, flags=re.IGNORECASE)
            return 15, text_clean  # Mặc định 15 phút
        
        return 15, text  # Mặc định 15 phút
    
    def _extract_location_advanced(self, text: str) -> Tuple[Optional[str], str]:
        """Trích xuất địa điểm và loại bỏ khỏi text"""
        patterns = [
            r'(?:tại|ở|chỗ|nơi)\s+([^,.\n!?]+?)(?=\s*$|\s+(?:lúc|vào|từ|đến|nhắc|báo))',
            r'(?:tại|ở|chỗ|nơi)\s+(.+?)(?=\s*$)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                location = match.group(1).strip()
                # Loại bỏ location khỏi text
                text_clean = text[:match.start()] + text[match.end():]
                return location, text_clean.strip()
        
        return None, text
    
    def _extract_time_advanced(self, text: str) -> Dict[str, Any]:
        """
        Trích xuất thông tin thời gian chi tiết
        Return: {
            'date_text': 'ngày mai', 'hôm nay', '10/11', ...
            'time_start': '09:00', '14h30', ...
            'time_end': '10:00', ... (optional)
            'raw_match': text đã match
        }
        """
        time_info = {
            'date_text': None,
            'time_start': None,
            'time_end': None,
            'raw_matches': [],
            'has_time_period': False  # Có "tối", "sáng", "chiều" không
        }
        
        # Kiểm tra có "tối", "sáng", "chiều" không
        if re.search(r'\b(tối|sáng|chiều|trưa|đêm)\b', text, re.IGNORECASE):
            time_info['has_time_period'] = True
        
        # 1. Tìm ngày (date)
        date_patterns = [
            # Ngày cụ thể: "10/11", "10-11", "10/11/2025"
            r'(\d{1,2}[/-]\d{1,2}(?:[/-]\d{2,4})?)',
            # Thứ: "thứ 2", "thứ hai", "t2"
            r'(thứ\s*\d|thứ\s+(?:hai|ba|tư|năm|sáu|bảy)|t\d|chủ\s+nhật|cn)',
            # Từ tương đối: "ngày mai", "hôm nay", "mai"
            r'(ngày\s+mai|hôm\s+nay|mai|ngày\s+kia|mốt)',
            # "tuần sau", "tuần này"
            r'(tuần\s+(?:sau|này|tới))',
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                time_info['date_text'] = match.group(1)
                time_info['raw_matches'].append(match.group(0))
                break
        
        # Nếu không tìm thấy ngày, mặc định là hôm nay
        if not time_info['date_text']:
            time_info['date_text'] = 'hôm nay'
        
        # 2. Tìm giờ (time) - chỉ tìm số giờ thật sự, không phải "8 giờ trước"
        time_patterns = [
            # 09:00, 14:30
            (r'(\d{1,2}:\d{2})', lambda m: m.group(1)),
            # 9h30, 14h15, 9h (nhưng không phải "8 giờ trước")
            (r'(\d{1,2})h(\d{0,2})(?!\s*trước)', lambda m: m.group(1) + 'h' + m.group(2)),
            # 9 giờ 30, 9giờ30 (nhưng không phải "8 giờ trước")
            (r'(\d{1,2})\s*giờ\s*(\d{0,2})(?!\s*trước)', lambda m: m.group(1) + 'giờ' + m.group(2)),
            # 9g30
            (r'(\d{1,2})g(\d{0,2})', lambda m: m.group(1) + 'g' + m.group(2)),
            # lúc 9, lúc 14
            (r'lúc\s+(\d{1,2})\b(?!.*giờ)', lambda m: m.group(1) + ':00'),
        ]
        
        time_matches = []
        for pattern, formatter in time_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                time_str = formatter(match)
                time_matches.append(time_str)
                time_info['raw_matches'].append(match.group(0))
        
        if time_matches:
            time_info['time_start'] = time_matches[0]
            if len(time_matches) > 1:
                time_info['time_end'] = time_matches[1]
        
        # 3. Tìm từ "từ ... đến ..."
        from_to_match = re.search(r'từ\s+(.+?)\s+đến\s+(.+?)(?=\s|$)', text, re.IGNORECASE)
        if from_to_match:
            time_info['time_start'] = from_to_match.group(1).strip()
            time_info['time_end'] = from_to_match.group(2).strip()
        
        return time_info
    
    def _extract_event_name_advanced(self, text: str, time_info: Dict) -> str:
        """Trích xuất tên sự kiện bằng cách loại bỏ tất cả các phần đã xác định"""
        cleaned = text
        
        # Loại bỏ tất cả các phần thời gian đã match
        for raw_match in time_info.get('raw_matches', []):
            cleaned = cleaned.replace(raw_match, '')
        
        # Loại bỏ các từ khóa thời gian còn sót
        time_keywords = [
            r'\b(?:vào|lúc|từ|đến|ngày|thời gian|khoảng|này|kia)\b',
            r'\b(?:sáng|chiều|tối|trưa|đêm)\b',
        ]
        for keyword in time_keywords:
            cleaned = re.sub(keyword, '', cleaned, flags=re.IGNORECASE)
        
        # Loại bỏ khoảng trắng thừa
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        # Loại bỏ dấu câu đầu cuối
        cleaned = cleaned.strip('.,!?;: ')
        
        # Viết hoa chữ cái đầu
        if cleaned:
            cleaned = cleaned[0].upper() + cleaned[1:]
        
        return cleaned if cleaned else "Sự kiện mới"
    def _build_datetime(self, time_info: Dict) -> Tuple[datetime, Optional[datetime]]:
        """Xây dựng datetime từ thông tin đã trích xuất"""
        now = datetime.now()
        
        # 1. Xác định ngày
        date_text = time_info.get('date_text', 'hôm nay').lower()
        base_date = now.date()
        
        # Xử lý các trường hợp ngày
        if date_text in ['hôm nay', 'bữa nay']:
            base_date = now.date()
        elif date_text in ['mai', 'ngày mai']:
            base_date = (now + timedelta(days=1)).date()
        elif date_text in ['ngày kia', 'mốt']:
            base_date = (now + timedelta(days=2)).date()
        elif 'thứ' in date_text or date_text in ['t2', 't3', 't4', 't5', 't6', 't7', 'cn']:
            # Xử lý thứ trong tuần
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
                if days_ahead == 0:  # Cùng ngày trong tuần
                    days_ahead = 7  # Tuần sau
                base_date = (now + timedelta(days=days_ahead)).date()
        
        elif re.match(r'\d{1,2}[/-]\d{1,2}', date_text):
            # Xử lý ngày dạng 10/11 hoặc 10-11
            try:
                parts = re.split(r'[/-]', date_text)
                day = int(parts[0])
                month = int(parts[1])
                year = now.year
                
                # Nếu có năm
                if len(parts) == 3:
                    year = int(parts[2])
                    if year < 100:
                        year += 2000
                
                base_date = datetime(year, month, day).date()
                
                # Nếu ngày đã qua trong năm nay, chuyển sang năm sau
                if base_date < now.date():
                    base_date = datetime(year + 1, month, day).date()
            except:
                base_date = now.date()
        
        # 2. Xác định giờ
        time_start = time_info.get('time_start')
        time_end = time_info.get('time_end')
        
        # Parse giờ bắt đầu
        hour_start, minute_start = self._parse_time_string(time_start)
        if hour_start is None:
            # Nếu có "tối", "sáng", "chiều" thì đoán giờ
            if time_info.get('has_time_period'):
                # Sẽ xử lý sau
                hour_start, minute_start = 19, 0  # Tối mặc định 19:00
            else:
                hour_start, minute_start = 9, 0  # Mặc định 9:00
        
        start_datetime = datetime.combine(base_date, datetime.min.time()).replace(
            hour=hour_start, minute=minute_start, second=0, microsecond=0
        )
        
        # Đảm bảo không trong quá khứ
        if start_datetime < now:
            # Nếu cùng ngày nhưng giờ đã qua, chuyển sang ngày mai
            if start_datetime.date() == now.date():
                start_datetime += timedelta(days=1)
        
        # Parse giờ kết thúc - CHỈ tạo end_datetime nếu có thông tin
        end_datetime = None
        if time_end:
            hour_end, minute_end = self._parse_time_string(time_end)
            if hour_end is not None:
                end_datetime = datetime.combine(base_date, datetime.min.time()).replace(
                    hour=hour_end, minute=minute_end, second=0, microsecond=0
                )
                
                # Đảm bảo end sau start
                if end_datetime <= start_datetime:
                    # Nếu end_time trước hoặc bằng start_time, thêm 1 ngày
                    end_datetime += timedelta(days=1)
                
                # Đảm bảo không trong quá khứ
                if end_datetime < now:
                    end_datetime += timedelta(days=1)
        
        # KHÔNG tạo end_datetime mặc định nếu không có thông tin
        # Giữ nguyên end_datetime = None
        
        return start_datetime, end_datetime

    def _parse_time_string(self, time_str: Optional[str]) -> Tuple[Optional[int], Optional[int]]:
        """Parse chuỗi thời gian thành giờ và phút"""
        if not time_str:
            return None, None
        
        time_str = time_str.strip().lower()
        
        # 09:00, 14:30
        match = re.match(r'(\d{1,2}):(\d{2})', time_str)
        if match:
            return int(match.group(1)), int(match.group(2))
        
        # 9h30, 14h15, 9h
        match = re.match(r'(\d{1,2})h(\d{0,2})', time_str)
        if match:
            hour = int(match.group(1))
            minute = int(match.group(2)) if match.group(2) else 0
            return hour, minute
        
        # 9 giờ 30, 9giờ30, 9 giờ
        match = re.match(r'(\d{1,2})\s*giờ\s*(\d{0,2})', time_str)
        if match:
            hour = int(match.group(1))
            minute = int(match.group(2)) if match.group(2) else 0
            return hour, minute
        
        # 9g30
        match = re.match(r'(\d{1,2})g(\d{0,2})', time_str)
        if match:
            hour = int(match.group(1))
            minute = int(match.group(2)) if match.group(2) else 0
            return hour, minute
        
        # Chỉ có số (9, 14)
        match = re.match(r'(\d{1,2})', time_str)
        if match:
            return int(match.group(1)), 0
        
        return None, None


