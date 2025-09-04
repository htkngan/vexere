class SimpleDatabase:
    """Database đơn giản để demo"""
    def __init__(self):
        self.schedules = [
            {
                'id': 'TN001',
                'departure': 'hà nội',
                'destination': 'sài gòn',
                'time': '08:00',
                'date': '2025-09-05',
                'available_seats': 50
            },
            {
                'id': 'TN002', 
                'departure': 'hà nội',
                'destination': 'sài gòn',
                'time': '09:00',  # THÊM CHUYẾN 9H
                'date': '2025-09-05',
                'available_seats': 30
            },
            {
                'id': 'TN003',
                'departure': 'hà nội',
                'destination': 'sài gòn',
                'time': '14:00',
                'date': '2025-09-05',
                'available_seats': 30
            },
            {
                'id': 'TN004',
                'departure': 'sài gòn',
                'destination': 'hà nội', 
                'time': '09:00',
                'date': '2025-09-05',
                'available_seats': 40
            }
        ]
        self.bookings = {}
    
    def find_available_schedules(self, departure, destination, date, quantity=1):
        """Tìm chuyến có sẵn"""
        available = []
        for schedule in self.schedules:
            if (schedule['departure'] == departure.lower() and 
                schedule['destination'] == destination.lower() and
                schedule['date'] == date and
                schedule['available_seats'] >= quantity):
                available.append(schedule)
        return available
    
    def book_ticket(self, schedule_id, quantity, passenger_info):
        """Đặt vé"""
        # Tìm schedule
        schedule = None
        for s in self.schedules:
            if s['id'] == schedule_id:
                schedule = s
                break
        
        if not schedule or schedule['available_seats'] < quantity:
            return None, "Không đủ chỗ trống"
        
        # Tạo mã vé
        ticket_code = f"VN{len(self.bookings)+1:06d}"
        
        # Lưu booking
        self.bookings[ticket_code] = {
            'ticket_code': ticket_code,
            'schedule_id': schedule_id,
            'departure': schedule['departure'],
            'destination': schedule['destination'],
            'time': schedule['time'],
            'date': schedule['date'],
            'quantity': quantity,
            'status': 'booked'
        }
        
        # Giảm ghế trống
        schedule['available_seats'] -= quantity
        
        return ticket_code, "Đặt vé thành công"
    
    def get_booking(self, ticket_code):
        """Lấy thông tin booking"""
        return self.bookings.get(ticket_code)
    
    def cancel_ticket(self, ticket_code):
        """Hủy vé"""
        booking = self.bookings.get(ticket_code)
        if not booking:
            return False, "Không tìm thấy vé"
        
        if booking['status'] == 'cancelled':
            return False, "Vé đã được hủy"
        
        # Hủy vé
        booking['status'] = 'cancelled'
        
        # Hoàn ghế
        for schedule in self.schedules:
            if schedule['id'] == booking['schedule_id']:
                schedule['available_seats'] += booking['quantity']
                break
        
        return True, "Hủy vé thành công"
    
    def change_time(self, ticket_code, new_time):
        """Đổi giờ"""
        booking = self.bookings.get(ticket_code)
        if not booking:
            return False, "Không tìm thấy vé"
        
        # Tìm chuyến mới cùng tuyến
        new_schedule = None
        for schedule in self.schedules:
            if (schedule['departure'] == booking['departure'] and
                schedule['destination'] == booking['destination'] and 
                schedule['time'] == new_time and
                schedule['available_seats'] >= booking['quantity']):
                new_schedule = schedule
                break
        
        if not new_schedule:
            return False, f"Không có chuyến lúc {new_time}"
        
        # Hoàn ghế cho chuyến cũ
        for schedule in self.schedules:
            if schedule['id'] == booking['schedule_id']:
                schedule['available_seats'] += booking['quantity']
                break
        
        # Đặt chỗ chuyến mới
        new_schedule['available_seats'] -= booking['quantity']
        booking['schedule_id'] = new_schedule['id']
        booking['time'] = new_time
        
        return True, f"Đổi giờ thành công sang {new_time}"

def normalize_time(time_str):
    """Chuẩn hóa format thời gian"""
    time_str = time_str.strip().lower()
    
    # Xử lý "9h" -> "09:00"
    if 'h' in time_str and ':' not in time_str:
        time_str = time_str.replace('h', ':00')
        if 'sáng' in time_str:
            time_str = time_str.replace(' sáng', '')
    
    # Xử lý "9" -> "09:00"  
    if ':' not in time_str and time_str.isdigit():
        hour = int(time_str)
        time_str = f"{hour:02d}:00"
    
    # Xử lý "9:0" -> "09:00"
    if ':' in time_str:
        parts = time_str.split(':')
        if len(parts) == 2:
            hour = int(parts[0])
            minute = int(parts[1])
            time_str = f"{hour:02d}:{minute:02d}"
    
    return time_str

# Khởi tạo database
db = SimpleDatabase()