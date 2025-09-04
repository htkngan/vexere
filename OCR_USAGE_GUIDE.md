# Hướng dẫn sử dụng OCR Ticket Extraction

## Mô tả
Script này sử dụng PaddleOCR để trích xuất thông tin từ ảnh vé xe khách tiếng Việt và tích hợp với NLP engine để xử lý thông tin.

## Cài đặt

### 1. Cài đặt dependencies
```bash
pip install -r requirements.txt
```

### 2. Hoặc cài đặt từng package
```bash
pip install paddleocr paddlepaddle Pillow opencv-python numpy fastapi
```

## Sử dụng

### 1. Import và khởi tạo
```python
from src.__modules.chatbot.image_extractor.image_handle import TicketImageExtractor
from src.__modules.chatbot.nlp_extractor.nlp_engine import ConversationManager

# Khởi tạo
extractor = TicketImageExtractor(use_gpu=False)  # Đặt True nếu có GPU
conversation = ConversationManager()
```

### 2. Trích xuất thông tin từ ảnh vé
```python
# Đường dẫn ảnh vé
image_path = "path/to/ticket.jpg"

# Trích xuất thông tin
result = extractor.extract_ticket_info(image_path)

if result['success']:
    ticket_data = result['data']
    print(f"Mã vé: {ticket_data.get('ticket_code')}")
    print(f"Tuyến đường: {ticket_data.get('departure')} → {ticket_data.get('destination')}")
    print(f"Thời gian: {ticket_data.get('departure_time')} ngày {ticket_data.get('departure_date')}")
else:
    print(f"Lỗi: {result['message']}")
```

### 3. Tích hợp với chatbot
```python
# Tạo text mô tả từ thông tin vé
booking_text = extractor.create_booking_text(result)

# Phân tích với NLP
from src.__modules.chatbot.nlp_extractor.nlp_engine import get_intent_entities_from_text
nlp_result = get_intent_entities_from_text(booking_text)

# Xử lý với conversation manager
response = conversation.process_turn(booking_text, nlp_result['intent'], nlp_result['entities'])
print(response['message'])
```

## Chạy demo

### Demo đơn giản
```bash
python demo_ocr_simple.py
```

### Demo đầy đủ
```bash
python test_ocr_integration.py
```

## Thông tin được trích xuất

Script có thể trích xuất các thông tin sau từ ảnh vé:

- **ticket_code**: Mã vé (VN123456)
- **departure**: Điểm khởi hành (Hà Nội)
- **destination**: Điểm đến (Sài Gòn)
- **departure_time**: Giờ khởi hành (08:00)
- **departure_date**: Ngày khởi hành (05/09/2025)
- **quantity**: Số lượng vé (2)
- **passenger_name**: Tên hành khách
- **phone**: Số điện thoại
- **price**: Giá vé

## Định dạng ảnh hỗ trợ

- JPEG (.jpg, .jpeg)
- PNG (.png)
- BMP (.bmp)
- TIFF (.tiff)

## Lưu ý

1. **Chất lượng ảnh**: Ảnh cần rõ nét, không bị mờ
2. **Ngôn ngữ**: Hỗ trợ tiếng Việt có dấu
3. **Hiệu suất**: 
   - CPU: ~2-5 giây/ảnh
   - GPU: ~0.5-1 giây/ảnh (nếu có CUDA)
4. **Bộ nhớ**: Cần ít nhất 2GB RAM

## Troubleshooting

### Lỗi import PaddleOCR
```bash
pip uninstall paddlepaddle paddleocr
pip install paddlepaddle-gpu  # Nếu có GPU
# hoặc
pip install paddlepaddle     # Chỉ CPU
pip install paddleocr
```

### Lỗi không đọc được ảnh
- Kiểm tra đường dẫn file
- Đảm bảo ảnh không bị corrupt
- Thử resize ảnh nếu quá lớn (>2000px)

### Độ chính xác thấp
- Tăng độ phân giải ảnh
- Cải thiện độ tương phản
- Đảm bảo text không bị nghiêng

## Ví dụ kết quả

```json
{
  "success": true,
  "message": "Trích xuất thông tin vé thành công",
  "data": {
    "ticket_code": "VN123456",
    "departure": "hà nội",
    "destination": "sài gòn",
    "departure_time": "08:00",
    "departure_date": "05/09/2025",
    "quantity": 2,
    "detected_intent": "dat_ve",
    "intent_confidence": 0.8
  },
  "raw_text": ["VÉ XE KHÁCH VEXERE", "Mã vé: VN123456", ...],
  "nlp_analysis": {
    "intent": "dat_ve",
    "entities": [...]
  }
}
```
