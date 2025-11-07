function processText() {
    const textInput = document.getElementById('textInput');
    const text = textInput.value.trim();
    
    if (!text) {
        alert('Vui lòng nhập văn bản mô tả sự kiện!');
        return;
    }
    
    fetch('/process_text', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({text: text})
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Hiển thị form xác nhận
            document.getElementById('eventName').value = data.event_name;
            document.getElementById('startTime').value = formatDateTimeForInput(data.start_time);
            document.getElementById('endTime').value = formatDateTimeForInput(data.end_time);
            document.getElementById('location').value = data.location || '';
            document.getElementById('timeReminder').value = data.time_reminder || 15;
            
            document.getElementById('confirmationSection').style.display = 'block';
        } else {
            alert('Lỗi: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Có lỗi xảy ra khi xử lý văn bản!');
    });
}

function formatDateTimeForInput(datetimeStr) {
    // Chuyển đổi định dạng datetime để hiển thị trong input
    const date = new Date(datetimeStr);
    return date.toISOString().slice(0, 16);
}

function addEvent() {
    const eventData = {
        event_name: document.getElementById('eventName').value,
        start_time: document.getElementById('startTime').value + ':00',
        end_time: document.getElementById('endTime').value + ':00',
        location: document.getElementById('location').value,
        time_reminder: document.getElementById('timeReminder').value
    };
    
    fetch('/add_event', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(eventData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Thêm sự kiện thành công!');
            document.getElementById('confirmationSection').style.display = 'none';
            document.getElementById('textInput').value = '';
            location.reload(); // Tải lại trang để hiển thị sự kiện mới
        } else {
            alert('Lỗi: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Có lỗi xảy ra khi thêm sự kiện!');
    });
}

function cancelEvent() {
    document.getElementById('confirmationSection').style.display = 'none';
    document.getElementById('eventForm').reset();
}