#!/usr/bin/env python3
"""
Test OCR với ảnh vé thật
"""

import os
import sys

# Setup environment
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.join(current_dir, 'src', '__modules', 'chatbot'))

def test_real_image_ocr():
    """Test OCR với ảnh thật"""
    print("📸 TEST OCR VỚI ẢNH THẬT")
    print("=" * 30)
    
    try:
        from src.__modules.chatbot.image_extractor.image_handle import TicketImageExtractor
        from src.__modules.chatbot.nlp_extractor.nlp_engine import ConversationManager, get_intent_entities_from_text
        
        # Khởi tạo OCR
        extractor = TicketImageExtractor()
        
        # Tìm ảnh test
        test_images = [
            'test_ticket.jpg',
            'ticket.png', 
            've.jpg',
            'sample_ticket.png'
        ]
        
        found_image = None
        for img in test_images:
            if os.path.exists(img):
                found_image = img
                break
        
        if not found_image:
            print("❌ Không tìm thấy ảnh test!")
            print("💡 Hãy đặt ảnh vé với tên:")
            for img in test_images:
                print(f"   - {img}")
            return False
        
        print(f"🔍 Đang xử lý ảnh: {found_image}")
        
        # Trích xuất thông tin
        result = extractor.extract_ticket_info(found_image)
        
        print(f"\n📋 KẾT QUẢ OCR:")
        print(f"Thành công: {result['success']}")
        print(f"Message: {result['message']}")
        
        if result['success']:
            print(f"\n📄 THÔNG TIN VÉ:")
            data = result['data']
            for key, value in data.items():
                print(f"  {key}: {value}")
            
            print(f"\n📝 RAW TEXT:")
            for i, line in enumerate(result['raw_text'], 1):
                print(f"  {i}: {line}")
            
            # Test với conversation
            print(f"\n🤖 TEST VỚI CONVERSATION MANAGER:")
            booking_text = extractor.create_booking_text(result)
            print(f"Booking text: {booking_text}")
            
            nlp_result = get_intent_entities_from_text(booking_text)
            print(f"Intent: {nlp_result['intent']}")
            print(f"Entities: {len(nlp_result['entities'])}")
            
            conversation = ConversationManager()
            response = conversation.process_turn(booking_text, nlp_result['intent'], nlp_result['entities'])
            
            print(f"Response: {response['message']}")
            print(f"Status: {response['status']}")
            
        return result['success']
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_test_instruction():
    """Tạo hướng dẫn test"""
    print("\n📝 HƯỚNG DẪN TEST VỚI ẢNH THẬT")
    print("=" * 40)
    print("1. Chụp ảnh vé xe hoặc tạo ảnh vé mẫu")
    print("2. Đảm bảo ảnh có thông tin rõ ràng:")
    print("   - Mã vé (VN123456)")
    print("   - Điểm đi (Hà Nội)")  
    print("   - Điểm đến (Sài Gòn)")
    print("   - Thời gian (08:00)")
    print("   - Ngày (05/09/2025)")
    print("   - Số vé (2)")
    print("3. Lưu ảnh với tên: test_ticket.jpg")
    print("4. Chạy script này để test")

if __name__ == "__main__":
    print("🎫 TEST OCR VỚI ẢNH VÉ THẬT")
    print("=" * 40)
    
    success = test_real_image_ocr()
    
    if not success:
        create_test_instruction()
    else:
        print("\n✅ Test thành công!")
        print("💡 OCR + NLP engine đã hoạt động tốt với ảnh thật!")
