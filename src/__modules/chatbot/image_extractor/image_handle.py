from paddleocr import PaddleOCR
import PIL
from PIL import Image
import re
import os
import sys
from datetime import datetime

# Import nlp_engine từ module cha
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from nlp_extractor.nlp_engine import get_intent_entities_from_text

class TicketImageExtractor:
    """Trích xuất thông tin vé từ hình ảnh sử dụng PaddleOCR"""
    
    def __init__(self, use_gpu=False):
        """Khởi tạo OCR engine
        Args:
            use_gpu: Sử dụng GPU hay không (mặc định False)
        """
        self.ocr = PaddleOCR(
            use_angle_cls=True,
            lang='vi'  # Tiếng Việt
        )
        
        # Patterns để nhận diện thông tin vé
        self.ticket_patterns = {
            'ticket_code': [
                re.compile(r'[A-Z]{2,3}\d{6,}', re.I),
                re.compile(r'Mã vé[:\s]*([A-Z0-9]+)', re.I),
                re.compile(r'Booking[:\s]*([A-Z0-9]+)', re.I)
            ],
            'departure': [
                re.compile(r'Từ[:\s]*([\w\s]+?)(?:\s*-|\s*đến)', re.I),
                re.compile(r'Khởi hành[:\s]*([\w\s]+?)(?:\s*-|\s*đến)', re.I),
                re.compile(r'Điểm đi[:\s]*([\w\s]+?)(?:\s*-|\s*đến)', re.I)
            ],
            'destination': [
                re.compile(r'Đến[:\s]*([\w\s]+?)(?:\s|$)', re.I),
                re.compile(r'Điểm đến[:\s]*([\w\s]+?)(?:\s|$)', re.I),
                re.compile(r'-\s*([\w\s]+?)(?:\s|$)', re.I)
            ],
            'departure_time': [
                re.compile(r'Giờ khởi hành[:\s]*(\d{1,2}:\d{2})', re.I),
                re.compile(r'Khởi hành[:\s]*(\d{1,2}:\d{2})', re.I),
                re.compile(r'(\d{1,2}:\d{2})', re.I)
            ],
            'departure_date': [
                re.compile(r'Ngày[:\s]*(\d{1,2}/\d{1,2}/\d{4})', re.I),
                re.compile(r'(\d{1,2}/\d{1,2}/\d{4})', re.I),
                re.compile(r'(\d{1,2}-\d{1,2}-\d{4})', re.I)
            ],
            'quantity': [
                re.compile(r'Số vé[:\s]*(\d+)', re.I),
                re.compile(r'Số lượng[:\s]*(\d+)', re.I),
                re.compile(r'(\d+)\s*vé', re.I)
            ],
            'passenger_name': [
                re.compile(r'Họ tên[:\s]*([\w\s]+?)(?:\s|$)', re.I),
                re.compile(r'Tên[:\s]*([\w\s]+?)(?:\s|$)', re.I)
            ],
            'phone': [
                re.compile(r'SĐT[:\s]*(\d{10,11})', re.I),
                re.compile(r'Điện thoại[:\s]*(\d{10,11})', re.I),
                re.compile(r'(\d{10,11})', re.I)
            ],
            'price': [
                re.compile(r'Giá[:\s]*([\d,\.]+)', re.I),
                re.compile(r'Thành tiền[:\s]*([\d,\.]+)', re.I),
                re.compile(r'([\d,\.]+)\s*VND', re.I)
            ]
        }
    
    def extract_text_from_image(self, image_path):
        """Trích xuất text từ hình ảnh
        Args:
            image_path: Đường dẫn tới file ảnh
        Returns:
            list: Danh sách các dòng text được OCR
        """
        try:
            # Kiểm tra file tồn tại
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Không tìm thấy file: {image_path}")
            
            # Thực hiện OCR
            result = self.ocr.ocr(image_path, cls=True)
            
            # Trích xuất text
            extracted_lines = []
            if result and result[0]:
                for line in result[0]:
                    if line and len(line) >= 2:
                        text = line[1][0]  # Text content
                        confidence = line[1][1]  # Confidence score
                        
                        # Chỉ lấy text có độ tin cậy >= 0.5
                        if confidence >= 0.5:
                            extracted_lines.append(text.strip())
            
            return extracted_lines
            
        except Exception as e:
            print(f"Lỗi khi OCR hình ảnh: {str(e)}")
            return []
    
    def extract_ticket_info(self, image_path):
        """Trích xuất thông tin vé từ hình ảnh
        Args:
            image_path: Đường dẫn tới file ảnh vé
        Returns:
            dict: Thông tin vé được trích xuất
        """
        # Trích xuất text từ hình ảnh
        text_lines = self.extract_text_from_image(image_path)
        
        if not text_lines:
            return {
                'success': False,
                'message': 'Không thể đọc được text từ hình ảnh',
                'data': {}
            }
        
        # Ghép tất cả text thành một chuỗi
        full_text = ' '.join(text_lines)
        print(f"📄 Text trích xuất được: {full_text}")
        
        # Trích xuất thông tin theo pattern
        ticket_info = {}
        
        for info_type, patterns in self.ticket_patterns.items():
            for pattern in patterns:
                match = pattern.search(full_text)
                if match:
                    if match.groups():
                        ticket_info[info_type] = match.group(1).strip()
                    else:
                        ticket_info[info_type] = match.group().strip()
                    break
        
        # Chuẩn hóa dữ liệu
        ticket_info = self._normalize_ticket_info(ticket_info)
        
        # Sử dụng NLP engine để trích xuất thêm thông tin
        nlp_result = get_intent_entities_from_text(full_text)
        
        # Kết hợp thông tin từ OCR và NLP
        final_info = self._merge_ocr_nlp_results(ticket_info, nlp_result)
        
        return {
            'success': True,
            'message': 'Trích xuất thông tin vé thành công',
            'data': final_info,
            'raw_text': text_lines,
            'nlp_analysis': nlp_result
        }
    
    def _normalize_ticket_info(self, info):
        """Chuẩn hóa thông tin vé"""
        normalized = info.copy()
        
        # Chuẩn hóa tên thành phố
        city_mapping = {
            'hà nội': 'hà nội',
            'ha noi': 'hà nội',
            'hanoi': 'hà nội',
            'sài gòn': 'sài gòn',
            'sai gon': 'sài gòn',
            'hồ chí minh': 'sài gòn',
            'ho chi minh': 'sài gòn',
            'hcm': 'sài gòn',
            'đà nẵng': 'đà nẵng',
            'da nang': 'đà nẵng',
            'danang': 'đà nẵng'
        }
        
        for field in ['departure', 'destination']:
            if field in normalized:
                city = normalized[field].lower().strip()
                for key, value in city_mapping.items():
                    if key in city:
                        normalized[field] = value
                        break
        
        # Chuẩn hóa thời gian
        if 'departure_time' in normalized:
            time_str = normalized['departure_time']
            # Đảm bảo format HH:MM
            if ':' in time_str:
                parts = time_str.split(':')
                if len(parts) == 2:
                    try:
                        hour = int(parts[0])
                        minute = int(parts[1])
                        normalized['departure_time'] = f"{hour:02d}:{minute:02d}"
                    except:
                        pass
        
        # Chuẩn hóa số lượng
        if 'quantity' in normalized:
            try:
                normalized['quantity'] = int(normalized['quantity'])
            except:
                normalized['quantity'] = 1
        
        return normalized
    
    def _merge_ocr_nlp_results(self, ocr_info, nlp_result):
        """Kết hợp kết quả OCR và NLP"""
        merged = ocr_info.copy()
        
        # Thêm thông tin từ NLP entities
        if nlp_result and 'entities' in nlp_result:
            for entity in nlp_result['entities']:
                entity_type = entity['entity']
                entity_value = entity['value']
                
                # Map NLP entities sang OCR fields
                if entity_type == 'departure' and 'departure' not in merged:
                    merged['departure'] = entity_value
                elif entity_type == 'destination' and 'destination' not in merged:
                    merged['destination'] = entity_value
                elif entity_type == 'time' and 'departure_time' not in merged:
                    merged['departure_time'] = entity_value
                elif entity_type == 'date' and 'departure_date' not in merged:
                    merged['departure_date'] = entity_value
                elif entity_type == 'quantity' and 'quantity' not in merged:
                    # Trích xuất số từ "X vé"
                    qty_match = re.search(r'(\d+)', entity_value)
                    if qty_match:
                        merged['quantity'] = int(qty_match.group(1))
                elif entity_type == 'ticket_code' and 'ticket_code' not in merged:
                    merged['ticket_code'] = entity_value
        
        # Thêm intent từ NLP
        if nlp_result and 'intent' in nlp_result:
            merged['detected_intent'] = nlp_result['intent']
            merged['intent_confidence'] = nlp_result.get('confidence', 0.0)
        
        return merged
    
    def create_booking_text(self, ticket_info):
        """Tạo text mô tả thông tin vé để sử dụng với conversation manager"""
        if not ticket_info or not ticket_info.get('success'):
            return "Không thể đọc thông tin vé từ hình ảnh"
        
        data = ticket_info.get('data', {})
        
        # Tạo câu mô tả đầy đủ
        description_parts = []
        
        if 'departure' in data and 'destination' in data:
            description_parts.append(f"đặt vé từ {data['departure']} đến {data['destination']}")
        
        if 'departure_time' in data:
            description_parts.append(f"lúc {data['departure_time']}")
        
        if 'departure_date' in data:
            description_parts.append(f"ngày {data['departure_date']}")
        
        if 'quantity' in data:
            description_parts.append(f"{data['quantity']} vé")
        
        if 'ticket_code' in data:
            description_parts.append(f"mã vé {data['ticket_code']}")
        
        return " ".join(description_parts)


def demo_ticket_extraction():
    """Demo function để test OCR vé"""
    extractor = TicketImageExtractor()
    
    # Test với một ảnh vé mẫu (nếu có)
    test_image_path = "test_ticket.jpg"
    
    if os.path.exists(test_image_path):
        print(f"🔍 Đang xử lý ảnh: {test_image_path}")
        result = extractor.extract_ticket_info(test_image_path)
        
        print("\n📋 Kết quả trích xuất:")
        print(f"Thành công: {result['success']}")
        print(f"Thông điệp: {result['message']}")
        
        if result['success']:
            print("\n📄 Thông tin vé:")
            for key, value in result['data'].items():
                print(f"  {key}: {value}")
            
            print(f"\n🤖 Text để sử dụng với chatbot:")
            booking_text = extractor.create_booking_text(result)
            print(f"  {booking_text}")
            
            # Test với NLP engine
            nlp_result = get_intent_entities_from_text(booking_text)
            print(f"\n🧠 Phân tích NLP:")
            print(f"  Intent: {nlp_result['intent']}")
            print(f"  Entities: {nlp_result['entities']}")
    else:
        print(f"❌ Không tìm thấy file test: {test_image_path}")
        print("💡 Để test, hãy đặt một ảnh vé tên 'test_ticket.jpg' trong thư mục hiện tại")


if __name__ == "__main__":
    demo_ticket_extraction()
