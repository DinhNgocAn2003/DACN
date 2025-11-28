import sys
import os
from datetime import datetime, timedelta
import re

# Thêm thư mục cha (backend) vào sys.path để import module nội bộ
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from nlp_processor import NLPProcessor

def normalize_text(text):
    """Chuẩn hóa text để so sánh (bỏ qua hoa thường và khoảng trắng thừa)"""
    if text is None:
        return ""
    return re.sub(r'\s+', ' ', str(text).strip().lower())

def check_match(actual, expected):
    """Kiểm tra khớp giữa kết quả thực tế và mong đợi"""
    return normalize_text(actual) == normalize_text(expected)

# Lấy ngày hiện tại để tính toán các ngày tương đối
now = datetime.now()
current_weekday = now.weekday()  # 0=Thứ 2, 1=Thứ 3, ..., 6=Chủ nhật

# Ngày mai và ngày kia
tomorrow = now + timedelta(days=1)
day_after_tomorrow = now + timedelta(days=2)

# Thứ 2 tuần sau: nếu hôm nay là thứ 2 thì tính thứ 2 tuần sau
days_until_next_monday = (7 - current_weekday) % 7
if days_until_next_monday == 0:
    days_until_next_monday = 7
next_monday = now + timedelta(days=days_until_next_monday)

# Thứ 6 tuần này: nếu hôm nay là thứ 6 thì tính thứ 6 tuần này, nếu là thứ 7, CN thì tính thứ 6 tuần sau
days_until_friday = (4 - current_weekday) % 7
if days_until_friday == 0:
    this_friday = now  # Hôm nay là thứ 6
else:
    this_friday = now + timedelta(days=days_until_friday)

# Thứ 7 tuần này: nếu hôm nay là thứ 7 thì tính thứ 7 tuần này, nếu là CN thì tính thứ 7 tuần sau
days_until_saturday = (5 - current_weekday) % 7
if days_until_saturday == 0:
    this_saturday = now  # Hôm nay là thứ 7
else:
    this_saturday = now + timedelta(days=days_until_saturday)

# Chủ nhật tuần này: nếu hôm nay là CN thì tính CN tuần này, nếu là thứ 2-6 thì tính CN tuần này
days_until_sunday = (6 - current_weekday) % 7
if days_until_sunday == 0:
    this_sunday = now  # Hôm nay là chủ nhật
else:
    this_sunday = now + timedelta(days=days_until_sunday)

# Danh sách test cases với expected results thực tế
testcases = [
    {
        "input": "Họp lớp lúc 9h 20/11 tại quán cafe X.",
        "target": {
            "event_name": "Họp lớp",
            "start_time": f"{now.year + 1}-11-20 09:00:00",
            "end_time": None,
            "location": "quán cafe X",
            "time_reminder": None
        }
    },
    {
        "input": "Nhắc tôi họp tại Văn Phòng Khoa vào 10/02/2026 lúc 9 giờ.",
        "target": {
            "event_name": "Họp",
            "start_time": "2026-02-10 09:00:00",
            "end_time": None,
            "location": "Văn Phòng Khoa",
            "time_reminder": None
        }
    },
    {
        "input": "Gặp bạn ở Văn Phòng Khoa ngày mai lúc 14:00.",
        "target": {
            "event_name": "Gặp bạn",
            "start_time": tomorrow.strftime("%Y-%m-%d 14:00:00"),
            "end_time": None,
            "location": "Văn Phòng Khoa",
            "time_reminder": None
        }
    },
    {
        "input": "Đi ăn với gia đình tối nay 19h tại nhà hàng Sakura.",
        "target": {
            "event_name": "Đi ăn với gia đình",
            "start_time": now.strftime("%Y-%m-%d 19:00:00"),
            "end_time": None,
            "location": "nhà hàng Sakura",
            "time_reminder": None
        }
    },
    {
        "input": "Hẹn bác sĩ 8 giờ sáng ngày 5 tháng 12 tại bệnh viện Tâm Đức.",
        "target": {
            "event_name": "Hẹn bác sĩ",
            "start_time": f"{now.year}-12-05 08:00:00",
            "end_time": None,
            "location": "bệnh viện Tâm Đức",
            "time_reminder": None
        }
    },
    {
        "input": "Sinh nhật Linh lúc 20h ngày 1/1 ở nhà.",
        "target": {
            "event_name": "Sinh nhật Linh",
            "start_time": f"{now.year + 1}-01-01 20:00:00",
            "end_time": None,
            "location": "nhà",
            "time_reminder": None
        }
    },
    {
        "input": "Họp team từ 9h đến 11h ngày 12/12 tại phòng 201.",
        "target": {
            "event_name": "Họp team",
            "start_time": f"{now.year}-12-12 09:00:00",
            "end_time": f"{now.year}-12-12 11:00:00",
            "location": "phòng 201",
            "time_reminder": None
        }
    },
    {
        "input": "Nhắc tôi 30 phút trước buổi thuyết trình lúc 15h ngày 3/3.",
        "target": {
            "event_name": "Buổi thuyết trình",
            "start_time": f"{now.year + 1}-03-03 15:00:00",
            "end_time": None,
            "location": None,
            "time_reminder": "30"
        }
    },
    {
        "input": "Đi xem phim ở CGV Vincom vào 20h ngày mai.",
        "target": {
            "event_name": "Đi xem phim",
            "start_time": tomorrow.strftime("%Y-%m-%d 20:00:00"),
            "end_time": None,
            "location": "CGV Vincom",
            "time_reminder": None
        }
    },
    {
        "input": "Dạy kèm tại quán cafe Mây lúc 14h ngày kia.",
        "target": {
            "event_name": "Dạy kèm",
            "start_time": day_after_tomorrow.strftime("%Y-%m-%d 14:00:00"),
            "end_time": None,
            "location": "quán cafe Mây",
            "time_reminder": None
        }
    },
    {
        "input": "Tập gym từ 6h đến 7h sáng mai.",
        "target": {
            "event_name": "Tập gym",
            "start_time": tomorrow.strftime("%Y-%m-%d 06:00:00"),
            "end_time": tomorrow.strftime("%Y-%m-%d 07:00:00"),
            "location": None,
            "time_reminder": None
        }
    },
    {
        "input": "Thi học kỳ 7h30 ngày 10/6 tại phòng thi 101.",
        "target": {
            "event_name": "Thi học kỳ",
            "start_time": f"{now.year + 1}-06-10 07:30:00",
            "end_time": None,
            "location": "phòng thi 101",
            "time_reminder": None
        }
    },
    {
        "input": "Làm bài kiểm tra lúc 9h ngày 5/5.",
        "target": {
            "event_name": "Làm bài kiểm tra",
            "start_time": f"{now.year + 1}-05-05 09:00:00",
            "end_time": None,
            "location": None,
            "time_reminder": None
        }
    },
    {
        "input": "Khám sức khỏe tổng quát lúc 8h ngày 2/2 tại bệnh viện A.",
        "target": {
            "event_name": "Khám sức khỏe tổng quát",
            "start_time": f"{now.year + 1}-02-02 08:00:00",
            "end_time": None,
            "location": "bệnh viện A",
            "time_reminder": None
        }
    },
    {
        "input": "Đi spa 15h ngày mốt.",
        "target": {
            "event_name": "Đi spa",
            "start_time": day_after_tomorrow.strftime("%Y-%m-%d 15:00:00"),
            "end_time": None,
            "location": None,
            "time_reminder": None
        }
    },
    {
        "input": "Dạy online lúc 19h30 tối nay.",
        "target": {
            "event_name": "Dạy online",
            "start_time": now.strftime("%Y-%m-%d 19:30:00"),
            "end_time": None,
            "location": None,
            "time_reminder": None
        }
    },
    {
        "input": "Đi siêu thị vào 17h ngày 2/4.",
        "target": {
            "event_name": "Đi siêu thị",
            "start_time": f"{now.year + 1}-04-02 17:00:00",
            "end_time": None,
            "location": None,
            "time_reminder": None
        }
    },
    {
        "input": "Làm bài tập nhóm 10 giờ sáng thứ hai tuần sau.",
        "target": {
            "event_name": "Làm bài tập nhóm",
            "start_time": next_monday.strftime("%Y-%m-%d 10:00:00"),
            "end_time": None,
            "location": None,
            "time_reminder": None
        }
    },
    {
        "input": "Uống cà phê với anh Minh lúc 16h chiều nay ở Highlands.",
        "target": {
            "event_name": "Uống cà phê với anh Minh",
            "start_time": now.strftime("%Y-%m-%d 16:00:00"),
            "end_time": None,
            "location": "Highlands",
            "time_reminder": None
        }
    },
    {
        "input": "Giao lưu câu lạc bộ lúc 18h thứ sáu tuần này tại hội trường.",
        "target": {
            "event_name": "Giao lưu câu lạc bộ",
            "start_time": this_saturday.strftime("%Y-%m-%d 18:00:00"),
            "end_time": None,
            "location": "hội trường",
            "time_reminder": None
        }
    },
    {
        "input": "Đón con lúc 17h30 ngày mai tại trường Tiểu Học A.",
        "target": {
            "event_name": "Đón con",
            "start_time": tomorrow.strftime("%Y-%m-%d 17:30:00"),
            "end_time": None,
            "location": "trường Tiểu Học A",
            "time_reminder": None
        }
    },
    {
        "input": "Đi công chứng giấy tờ lúc 8h ngày 14/7.",
        "target": {
            "event_name": "Đi công chứng giấy tờ",
            "start_time": f"{now.year + 1}-07-14 08:00:00",
            "end_time": None,
            "location": None,
            "time_reminder": None
        }
    },
    {
        "input": "Tham dự workshop vào 9h ngày 21/10 tại trung tâm B.",
        "target": {
            "event_name": "Tham dự workshop",
            "start_time": f"{now.year + 1}-10-21 09:00:00",
            "end_time": None,
            "location": "trung tâm B",
            "time_reminder": None
        }
    },
    {
        "input": "Đi siêu âm lúc 7h sáng ngày 3/1 ở bệnh viện C.",
        "target": {
            "event_name": "Đi siêu âm",
            "start_time": f"{now.year + 1}-01-03 07:00:00",
            "end_time": None,
            "location": "bệnh viện C",
            "time_reminder": None
        }
    },
    {
        "input": "Mua quà sinh nhật lúc 19h tối thứ bảy tuần này.",
        "target": {
            "event_name": "Mua quà sinh nhật",
            "start_time": this_saturday.strftime("%Y-%m-%d 19:00:00"),
            "end_time": None,
            "location": None,
            "time_reminder": None
        }
    },
    {
        "input": "Phỏng vấn xin việc 15h ngày 9/9 tại công ty TNHH XYZ.",
        "target": {
            "event_name": "Phỏng vấn xin việc",
            "start_time": f"{now.year + 1}-09-09 15:00:00",
            "end_time": None,
            "location": "công ty TNHH XYZ",
            "time_reminder": None
        }
    },
    {
        "input": "Đi lễ lúc 5h sáng chủ nhật.",
        "target": {
            "event_name": "Đi lễ",
            "start_time": this_sunday.strftime("%Y-%m-%d 05:00:00"),
            "end_time": None,
            "location": None,
            "time_reminder": None
        }
    },
    {
        "input": "Tập văn nghệ vào 19h ngày 22/12 ở phòng đa năng.",
        "target": {
            "event_name": "Tập văn nghệ",
            "start_time": f"{now.year + 1}-12-22 19:00:00",
            "end_time": None,
            "location": "phòng đa năng",
            "time_reminder": None
        }
    },
    {
        "input": "Kiểm tra mắt lúc 10h ngày 12/8 tại cửa hàng mắt kính.",
        "target": {
            "event_name": "Kiểm tra mắt",
            "start_time": f"{now.year + 1}-08-12 10:00:00",
            "end_time": None,
            "location": "cửa hàng mắt kính",
            "time_reminder": None
        }
    },
    {
        "input": "Gặp đối tác lúc 8h30 ngày mốt tại công ty ABC.",
        "target": {
            "event_name": "Gặp đối tác",
            "start_time": day_after_tomorrow.strftime("%Y-%m-%d 08:30:00"),
            "end_time": None,
            "location": "công ty ABC",
            "time_reminder": None
        }
    }
]

def run_nlp_tests():
    """Chạy test và tính độ chính xác của NLP processor"""
    p = NLPProcessor()
    correct_count = 0
    total_count = len(testcases)
    
    print("🧪 BẮT ĐẦU KIỂM TRA NLP PROCESSOR")
    print("=" * 80)
    
    for i, test_case in enumerate(testcases, 1):
        input_text = test_case["input"]
        target = test_case["target"]
        
        print(f"Test {i:2d}: {input_text}")
        
        # Chạy NLP processor
        result = p.process_text(input_text)
        
        # Kiểm tra từng trường
        fields_correct = 0
        total_fields = 5
        incorrect_fields = []
        
        for field in ["event_name", "start_time", "end_time", "location", "time_reminder"]:
            actual_value = result.get(field)
            expected_value = target[field]
            
            is_match = check_match(actual_value, expected_value)
            if is_match:
                fields_correct += 1
            else:
                incorrect_fields.append(field)
                print(f"   ❌ {field}:")
                print(f"      Expected: {expected_value}")
                print(f"      Actual:   {actual_value}")
        
        # Nếu tất cả fields đều khớp
        if fields_correct == total_fields:
            correct_count += 1
            print(f"   ✅ ĐÚNG ({fields_correct}/{total_fields} fields)")
        else:
            incorrect = total_fields - fields_correct
            print(f"   ❌ SAI ({incorrects}/{total_fields} fields) - Lỗi: {', '.join(incorrect_fields)}")
        
        print("-" * 60)
    
    # Tính toán kết quả tổng
    accuracy = (correct_count / total_count) * 100
    print("\n" + "=" * 80)
    print(f"KẾT QUẢ TỔNG QUÁT:")
    print(f"   Tổng số test cases: {total_count}")
    print(f"   Số lần đúng:        {correct_count}")
    print(f"   Số lần sai:         {total_count - correct_count}")
    print(f"   Độ chính xác:       {accuracy:.1f}%")
    print("=" * 80)
    
    return correct_count, total_count, accuracy

if __name__ == "__main__":
    run_nlp_tests()