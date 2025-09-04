import re
from datetime import datetime, timedelta

# Patterns để nhận diện intent và entities
INTENT_PATTERNS = {
    'dat_ve': re.compile(r'đặt|mua|book.*vé', re.I),
    'huy_ve': re.compile(r'hủy|cancel|trả|huỷ.*vé', re.I),
    'doi_gio': re.compile(r'đổi|thay đổi|chuyển.*giờ', re.I),
    'xuat_hoa_don': re.compile(r'xuất|hóa đơn|bill', re.I),
    'khieu_nai': re.compile(r'khiếu nại|phản ánh|than phiền', re.I)
}

ENTITY_PATTERNS = {
    'time': re.compile(r'\d{1,2}:\d{2}|\d{1,2}h(?:\s*sáng|\s*chiều|\s*tối)?', re.I),
    'date': re.compile(r'ngày mai|hôm nay|mai|\d{1,2}/\d{1,2}', re.I),
    'ticket_code': re.compile(r'[A-Z]{2,3}\d{6,}', re.I),
    'quantity': re.compile(r'(\d+)\s*vé', re.I),
    'city': re.compile(r'hà nội|sài gòn|đà nẵng|hồ chí minh|huế|cần thơ|hải phòng', re.I)
}

def get_intent_entities_from_text(text):
    """Phân tích intent và entities từ text"""
    text_lower = text.lower()
    
    # Tìm intent
    intent = 'unknown'
    for intent_name, pattern in INTENT_PATTERNS.items():
        if pattern.search(text_lower):
            intent = intent_name
            break
    
    # Tìm entities
    entities = []
    
    # Tìm time
    for match in ENTITY_PATTERNS['time'].finditer(text_lower):
        entities.append({
            'entity': 'time',
            'value': match.group().strip(),
            'confidence': 0.8
        })
    
    # Tìm date
    for match in ENTITY_PATTERNS['date'].finditer(text_lower):
        entities.append({
            'entity': 'date', 
            'value': match.group().strip(),
            'confidence': 0.8
        })
    
    # Tìm quantity
    for match in ENTITY_PATTERNS['quantity'].finditer(text_lower):
        entities.append({
            'entity': 'quantity',
            'value': match.group().strip(),
            'confidence': 0.8
        })
    
    # Tìm ticket_code
    for match in ENTITY_PATTERNS['ticket_code'].finditer(text):
        entities.append({
            'entity': 'ticket_code',
            'value': match.group().strip(),
            'confidence': 0.8
        })
    
    # Xử lý location đặc biệt - SỬA LẠI
    if 'từ' in text_lower and 'đến' in text_lower:
        # Pattern: "từ X đến Y"
        location_match = re.search(r'từ\s+([\w\s]+?)\s+đến\s+([\w\s]+?)(?:\s+lúc|\s+vào|\s+ngày|$)', text_lower)
        if location_match:
            departure = location_match.group(1).strip()
            destination = location_match.group(2).strip()
            entities.append({
                'entity': 'departure',
                'value': departure,
                'confidence': 0.8
            })
            entities.append({
                'entity': 'destination', 
                'value': destination,
                'confidence': 0.8
            })
    elif 'đi' in text_lower:
        # Pattern: "đi X" - SỬA LẠI để không bao gồm thời gian
        go_match = re.search(r'đi\s+([\w\s]+?)(?:\s+lúc|\s+vào|\s+ngày|$)', text_lower)
        if go_match:
            destination = go_match.group(1).strip()
            entities.append({
                'entity': 'destination',
                'value': destination,
                'confidence': 0.8
            })
    
    return {
        'intent': intent,
        'entities': entities,
        'confidence': 0.8 if intent != 'unknown' else 0.0
    }

class ConversationState:
    """Lưu trạng thái cuộc hội thoại"""
    def __init__(self):
        self.current_intent = None
        self.collected_entities = {}
        self.conversation_history = []
        self.completed_actions = {}
    
    def add_to_history(self, user_input, intent, entities):
        self.conversation_history.append({
            'user_input': user_input,
            'intent': intent,
            'entities': entities
        })
    
    def reset_current_flow(self):
        self.current_intent = None
        self.collected_entities = {}

class SimpleDatabase:
    """Database đơn giản để demo"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SimpleDatabase, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        
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

class ConversationManager:
    """Quản lý cuộc hội thoại"""
    def __init__(self):
        self.state = ConversationState()
        self.db = SimpleDatabase()
        
        # Entity bắt buộc cho mỗi intent
        self.required_entities = {
            'dat_ve': ['departure', 'destination', 'date', 'quantity', 'time'],
            'huy_ve': ['ticket_code'],
            'doi_gio': ['ticket_code', 'new_time'],
            'xuat_hoa_don': ['ticket_code'],
            'khieu_nai': ['ticket_code', 'complaint_content']
        }
        
        # Câu hỏi cho từng entity
        self.entity_questions = {
            'departure': "Bạn muốn đi từ đâu?",
            'destination': "Bạn muốn đến đâu?",
            'time': "Bạn muốn đi lúc mấy giờ?", 
            'date': "Bạn muốn đi ngày nào?",
            'quantity': "Bạn muốn đặt bao nhiêu vé?",
            'ticket_code': "Vui lòng cung cấp mã vé của bạn.",
            'new_time': "Bạn muốn đổi sang giờ nào?",
            'complaint_content': "Vui lòng mô tả chi tiết vấn đề bạn gặp phải."
        }
    
    def process_turn(self, user_input, intent, entities):
        """Xử lý một lượt hội thoại"""
        # Lưu lịch sử
        self.state.add_to_history(user_input, intent, entities)
        
        # Nếu có intent mới
        if intent != 'unknown' and intent != self.state.current_intent:
            if self.state.current_intent:
                print(f"   🔄 Chuyển từ '{self.state.current_intent}' sang '{intent}'")
            self.state.reset_current_flow()
            self.state.current_intent = intent
        
        # Set intent nếu chưa có
        if not self.state.current_intent and intent != 'unknown':
            self.state.current_intent = intent
        
        # Thu thập entities
        for entity in entities:
            entity_type = entity['entity']
            if entity_type == 'time' and self.state.current_intent == 'doi_gio':
                self.state.collected_entities['new_time'] = entity['value']
            else:
                self.state.collected_entities[entity_type] = entity['value']
        
        # Xử lý câu trả lời khi intent = unknown (chỉ khi không có entities nào được phân tích)
        if intent == 'unknown' and self.state.current_intent and not entities:
            self._handle_answer(user_input)
        
        # Sử dụng thông tin từ action trước
        self._use_previous_actions()
        
        return self._check_and_respond()
    
    def _handle_answer(self, user_input):
        """Xử lý câu trả lời cho entity đang thiếu"""
        required = self.required_entities.get(self.state.current_intent, [])
        missing = [e for e in required if e not in self.state.collected_entities]
        
        if not missing:
            return
        
        next_entity = missing[0]
        user_input = user_input.strip()
        
        print(f"   🔧 [Debug] Xử lý entity '{next_entity}' với input '{user_input}'")
        
        if next_entity in ['departure', 'destination']:
            # Tìm tên thành phố
            city_match = ENTITY_PATTERNS['city'].search(user_input.lower())
            if city_match:
                self.state.collected_entities[next_entity] = city_match.group()
            else:
                self.state.collected_entities[next_entity] = user_input.lower()
        
        elif next_entity in ['time', 'new_time']:
            # Xử lý time hoặc new_time
            time_match = ENTITY_PATTERNS['time'].search(user_input.lower())
            if time_match:
                self.state.collected_entities[next_entity] = time_match.group()
            else:
                # Nếu user nhập "8" hay "14:00" đều được
                self.state.collected_entities[next_entity] = user_input
        
        elif next_entity == 'date':
            date_match = ENTITY_PATTERNS['date'].search(user_input.lower())
            if date_match:
                self.state.collected_entities['date'] = date_match.group()
            elif 'mai' in user_input.lower():
                self.state.collected_entities['date'] = 'ngày mai'
            else:
                self.state.collected_entities['date'] = user_input
        
        elif next_entity == 'quantity':
            num_match = re.search(r'\d+', user_input)
            if num_match:
                self.state.collected_entities['quantity'] = num_match.group() + ' vé'
            else:
                self.state.collected_entities['quantity'] = '1 vé'  # Default
        
        elif next_entity == 'ticket_code':
            ticket_match = ENTITY_PATTERNS['ticket_code'].search(user_input)
            if ticket_match:
                self.state.collected_entities['ticket_code'] = ticket_match.group()
            else:
                self.state.collected_entities['ticket_code'] = user_input.upper()
        
        elif next_entity == 'complaint_content':
            self.state.collected_entities['complaint_content'] = user_input
    
    def _use_previous_actions(self):
        """Sử dụng thông tin từ action trước đó"""
        current_intent = self.state.current_intent
        
        if current_intent in ['huy_ve', 'doi_gio', 'xuat_hoa_don'] and 'ticket_code' not in self.state.collected_entities:
            if 'dat_ve' in self.state.completed_actions:
                booking = self.state.completed_actions['dat_ve']
                if 'ticket_code' in booking:
                    self.state.collected_entities['ticket_code'] = booking['ticket_code']
                    print(f"   🔗 Sử dụng mã vé: {booking['ticket_code']}")
    
    def _check_and_respond(self):
        """Kiểm tra thông tin và trả về response"""
        if not self.state.current_intent:
            return {
                'status': 'need_intent',
                'message': "Tôi chưa hiểu bạn muốn làm gì. Bạn có thể nói rõ hơn không?"
            }
        
        required = self.required_entities.get(self.state.current_intent, [])
        missing = [e for e in required if e not in self.state.collected_entities]
        
        if missing:
            next_entity = missing[0]
            question = self.entity_questions.get(next_entity, f"Vui lòng cung cấp {next_entity}")
            return {
                'status': 'need_more_info',
                'message': question,
                'collected': dict(self.state.collected_entities),
                'missing': missing
            }
        else:
            return self._execute_action()
    
    def _execute_action(self):
        """Thực hiện hành động"""
        intent = self.state.current_intent
        entities = self.state.collected_entities
        
        if intent == 'dat_ve':
            return self._book_ticket(entities)
        elif intent == 'huy_ve':
            return self._cancel_ticket(entities)
        elif intent == 'doi_gio':
            return self._change_time(entities)
        elif intent == 'xuat_hoa_don':
            return self._export_invoice(entities)
        elif intent == 'khieu_nai':
            return self._handle_complaint(entities)
        
        self.state.reset_current_flow()
        return {
            'status': 'completed',
            'message': "Hành động không được hỗ trợ."
        }
    
    def _book_ticket(self, entities):
        """Đặt vé"""
        departure = entities['departure']
        destination = entities['destination']
        date = self._parse_date(entities['date'])
        quantity = int(entities['quantity'].replace('vé', '').strip())
        
        # Tìm chuyến
        schedules = self.db.find_available_schedules(departure, destination, date, quantity)
        
        if not schedules:
            return {
                'status': 'failed',
                'message': f"Không có chuyến từ {departure} đến {destination} ngày {date}"
            }
        
        # Chọn chuyến theo thời gian
        selected = None
        if 'time' in entities:
            time = normalize_time(entities['time'])  # Sử dụng hàm normalize_time
            
            for s in schedules:
                if s['time'] == time:
                    selected = s
                    break
            
            if not selected:
                times = [s['time'] for s in schedules]
                return {
                    'status': 'need_more_info',
                    'message': f"Không có chuyến lúc {time}. Giờ có sẵn: {', '.join(times)}",
                    'available_options': times
                }
        else:
            selected = schedules[0]
        
        # Đặt vé
        ticket_code, msg = self.db.book_ticket(selected['id'], quantity, {})
        
        if ticket_code:
            # Lưu thông tin
            self.state.completed_actions['dat_ve'] = {
                'ticket_code': ticket_code,
                'departure': departure,
                'destination': destination,
                'time': selected['time'],
                'date': date,
                'quantity': quantity
            }
            
            message = f"✅ Đặt vé thành công!\n"
            message += f"Mã vé: {ticket_code}\n"
            message += f"Tuyến: {departure} → {destination}\n"
            message += f"Thời gian: {selected['time']} ngày {date}\n"
            message += f"Số vé: {quantity}"
        else:
            message = f"❌ Đặt vé thất bại: {msg}"
        
        self.state.reset_current_flow()
        return {
            'status': 'completed',
            'message': message,
            'executed_action': 'dat_ve'
        }
    
    def _cancel_ticket(self, entities):
        """Hủy vé"""
        ticket_code = entities['ticket_code']
        success, msg = self.db.cancel_ticket(ticket_code)
        
        self.state.reset_current_flow()
        return {
            'status': 'completed',
            'message': f"✅ {msg}" if success else f"❌ {msg}",
            'executed_action': 'huy_ve'
        }
    
    def _change_time(self, entities):
        """Đổi giờ"""
        ticket_code = entities['ticket_code']
        new_time = normalize_time(entities['new_time'])  # Sử dụng hàm normalize_time
        
        success, msg = self.db.change_time(ticket_code, new_time)
        
        self.state.reset_current_flow()
        return {
            'status': 'completed',
            'message': f"✅ {msg}" if success else f"❌ {msg}",
            'executed_action': 'doi_gio'
        }
    
    def _export_invoice(self, entities):
        """Xuất hóa đơn"""
        ticket_code = entities['ticket_code']
        booking = self.db.get_booking(ticket_code)
        
        if not booking:
            message = "❌ Không tìm thấy vé"
        elif booking.get('status') == 'cancelled':
            message = "❌ Không thể xuất hóa đơn cho vé đã hủy"
        else:
            message = f"📄 Hóa đơn vé {ticket_code}\n"
            message += f"Tuyến: {booking['departure']} → {booking['destination']}\n"
            message += f"Thời gian: {booking['time']} ngày {booking['date']}\n"
            message += f"Số vé: {booking['quantity']}"
        
        self.state.reset_current_flow()
        return {
            'status': 'completed',
            'message': message,
            'executed_action': 'xuat_hoa_don'
        }
    
    def _handle_complaint(self, entities):
        """Xử lý khiếu nại"""
        ticket_code = entities['ticket_code']
        complaint = entities['complaint_content']
        
        booking = self.db.get_booking(ticket_code)
        if not booking:
            message = "❌ Không tìm thấy vé để khiếu nại"
        else:
            message = f"📝 Đã ghi nhận khiếu nại cho vé {ticket_code}\n"
            message += f"Nội dung: {complaint}\n"
            message += f"Chúng tôi sẽ xử lý trong 24h."
        
        self.state.reset_current_flow()
        return {
            'status': 'completed',
            'message': message,
            'executed_action': 'khieu_nai'
        }
    
    def _parse_date(self, date_str):
        """Chuyển đổi ngày - SỬA LẠI"""
        date_str = date_str.lower().strip()
        if 'ngày mai' in date_str or date_str == 'mai':
            tomorrow = datetime.now() + timedelta(days=1)
            return tomorrow.strftime('%Y-%m-%d')
        elif 'hôm nay' in date_str:
            return datetime.now().strftime('%Y-%m-%d')
        else:
            # Thử parse DD/MM format
            if '/' in date_str:
                try:
                    parts = date_str.split('/')
                    if len(parts) == 2:
                        day, month = int(parts[0]), int(parts[1])
                        year = datetime.now().year
                        return f"{year}-{month:02d}-{day:02d}"
                except:
                    pass
        return '2025-09-05'  # Default demo