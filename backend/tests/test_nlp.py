import sys
import os
from datetime import datetime

# Đảm bảo đường dẫn tới thư mục backend để import các module nội bộ
HERE = os.path.dirname(__file__)
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from nlp_processor import NLPProcessor
from nlp.preprocess import remove_diacritics


# Mảng 30 test case: mỗi case có 'text' và 'expected' chứa các trường
# event_name, start_time, end_time, location, time_reminder
# Nếu một giá trị trong expected là None thì sẽ không kiểm tra trường đó
TEST_CASES = [
    {"text": "gap nhom luc 14h o phong hop 301", "expected": {"event_name": None, "start_time": None, "end_time": None, "location": None, "time_reminder": None}},
    {"text": "Sinh nhật mẹ vào 10/11, cả ngày", "expected": {"event_name": None, "start_time": None, "end_time": None, "location": None, "time_reminder": None}},
    {"text": "Họp dự án vào 25/12/2025 lúc 09:30 tại phòng 201", "expected": {"event_name": None, "start_time": None, "end_time": None, "location": None, "time_reminder": None}},
    {"text": "Từ 10h đến 12h ngày 01/01/2026 họp đào tạo", "expected": {"event_name": None, "start_time": None, "end_time": None, "location": None, "time_reminder": None}},
    {"text": "Buổi họp ngày 1 tháng 6 năm 2026 lúc 15:00", "expected": {"event_name": None, "start_time": None, "end_time": None, "location": None, "time_reminder": None}},
    {"text": "Tiệc liên hoan 20/07/2026 19:00 tại nhà hàng", "expected": {"event_name": None, "start_time": None, "end_time": None, "location": None, "time_reminder": None}},
    {"text": "Họp nhóm thứ hai 02/02/2026 08:00 ở phòng họp", "expected": {"event_name": None, "start_time": None, "end_time": None, "location": None, "time_reminder": None}},
    {"text": "Gặp khách hàng vào 15/03/2026 tại 123 Đường Lê Lợi, quận 1", "expected": {"event_name": None, "start_time": None, "end_time": None, "location": None, "time_reminder": None}},
    {"text": "Hẹn gặp Bác sĩ Nguyễn Văn A vào 05/05/2026 10:00", "expected": {"event_name": None, "start_time": None, "end_time": None, "location": None, "time_reminder": None}},
    {"text": "Nhắc 14:00 gọi điện", "expected": {"event_name": None, "start_time": None, "end_time": None, "location": None, "time_reminder": None}},
    {"text": "Kỷ niệm công ty 12/12/2026", "expected": {"event_name": None, "start_time": None, "end_time": None, "location": None, "time_reminder": None}},
    {"text": "Buổi phỏng vấn 03/08/2026 09:45, phòng A2", "expected": {"event_name": None, "start_time": None, "end_time": None, "location": None, "time_reminder": None}},
    {"text": "Hội thảo từ 10/09/2026 đến 12/09/2026", "expected": {"event_name": None, "start_time": None, "end_time": None, "location": None, "time_reminder": None}},
    {"text": "Thảo luận tại văn phòng Hà Nội hoặc chi nhánh Sài Gòn 20/10/2026", "expected": {"event_name": None, "start_time": None, "end_time": None, "location": None, "time_reminder": None}},
    {"text": "Gặp gỡ 01.11.2026 14:00 ở quán cà phê", "expected": {"event_name": None, "start_time": None, "end_time": None, "location": None, "time_reminder": None}},
    {"text": "Họp tổng kết 2026-12-31 16:00", "expected": {"event_name": None, "start_time": None, "end_time": None, "location": None, "time_reminder": None}},
    {"text": "Buổi tối 24/12/2026 gặp bạn bè", "expected": {"event_name": None, "start_time": None, "end_time": None, "location": None, "time_reminder": None}},
    {"text": "Team building, 11/11/2026, bắt đầu lúc 08:00, tập trung sân trường", "expected": {"event_name": None, "start_time": None, "end_time": None, "location": None, "time_reminder": None}},
    {"text": "Bắt đầu dự án 01/01/2026 00:00", "expected": {"event_name": None, "start_time": None, "end_time": None, "location": None, "time_reminder": None}},
    {"text": "Kiểm tra server 05/05/2026 12:30:15", "expected": {"event_name": None, "start_time": None, "end_time": None, "location": None, "time_reminder": None}},
    {"text": "Gặp gỡ Đại diện công ty Á Châu 07/07/2026 10:00", "expected": {"event_name": None, "start_time": None, "end_time": None, "location": None, "time_reminder": None}},
    {"text": "Có họp không vào 12/12/2026?", "expected": {"event_name": None, "start_time": None, "end_time": None, "location": None, "time_reminder": None}},
    {"text": "Chọn 20/10/2026 hoặc 21/10/2026 cho sự kiện", "expected": {"event_name": None, "start_time": None, "end_time": None, "location": None, "time_reminder": None}},
    {"text": "HỌP BAN LÃNH ĐẠO 02/02/2026 14:00", "expected": {"event_name": None, "start_time": None, "end_time": None, "location": None, "time_reminder": None}},
    {"text": "Sự kiện 5 Jan 2026 10:00 tại hội trường", "expected": {"event_name": None, "start_time": None, "end_time": None, "location": None, "time_reminder": None}},
    {"text": "Họp vào ngày thứ 3, 14/04/2026 09:00", "expected": {"event_name": None, "start_time": None, "end_time": None, "location": None, "time_reminder": None}},
    {"text": "Nhắc việc: kiểm tra báo cáo tài chính cuối quý", "expected": {"event_name": None, "start_time": None, "end_time": None, "location": None, "time_reminder": None}},
    {"text": "Họp: bàn giao dự án - 30/09/2026 10:00", "expected": {"event_name": None, "start_time": None, "end_time": None, "location": None, "time_reminder": None}},
    {"text": "Gap nhom luc 14:00, phong 301", "expected": {"event_name": None, "start_time": None, "end_time": None, "location": None, "time_reminder": None}},
]


proc = NLPProcessor()
errors = []
for idx, case in enumerate(TEST_CASES, start=1):
    text = case["text"]
    expected = case.get("expected", {})
    res = proc.process_text(text)

    # ensure processing returned success by default
    if not res.get("success"):
        errors.append(f"case {idx} processing failed: {text} -> {res}")
        continue

    # for each expected field, if expected is not None, compare
    # event_name and location use substring check (diacritics-insensitive)
    ev_expected = expected.get("event_name")
    if ev_expected is not None:
        ev = res.get("event_name") or ""
        if ev_expected.lower() not in remove_diacritics(ev.lower()):
            errors.append(f"case {idx} event_name mismatch: {text} -> got '{ev}', expected contains '{ev_expected}'")

    start_expected = expected.get("start_time")
    if start_expected is not None:
        if res.get("start_time") != start_expected:
            errors.append(f"case {idx} start_time mismatch: {text} -> got '{res.get('start_time')}', expected '{start_expected}'")

    end_expected = expected.get("end_time")
    if end_expected is not None:
        if res.get("end_time") != end_expected:
            errors.append(f"case {idx} end_time mismatch: {text} -> got '{res.get('end_time')}', expected '{end_expected}'")

    loc_expected = expected.get("location")
    if loc_expected is not None:
        loc = res.get("location") or ""
        if loc_expected.lower() not in remove_diacritics(loc.lower()):
            errors.append(f"case {idx} location mismatch: {text} -> got '{loc}', expected contains '{loc_expected}'")

    reminder_expected = expected.get("time_reminder")
    if reminder_expected is not None:
        if res.get("time_reminder") != reminder_expected:
            errors.append(f"case {idx} time_reminder mismatch: {text} -> got '{res.get('time_reminder')}', expected '{reminder_expected}'")

total = len(TEST_CASES)
failed = len(errors)
passed = total - failed
summary = f"Passed {passed}/{total} cases."
print(summary)
if errors:
    raise AssertionError(summary + "\n" + "\n".join(errors))
