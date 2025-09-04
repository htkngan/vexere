import dotenv
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, project_root)

from src.__modules.chatbot.nlp_extractor.nlp_engine import get_intent_entities_from_text, ConversationManager
from src.database.schemas import db

dotenv.load_dotenv()

class Signal:
    def __init__(self, context=None):
        self.context = context
        if context:
            result = get_intent_entities_from_text(context)
            self.intent = result['intent']
            self.entities = result['entities']
        else:
            self.intent = 'unknown'
            self.entities = []

def main(user_query=None, signal=None):
    """Xử lý một lượt hội thoại cho đặt vé/dịch vụ"""
    # Khởi tạo conversation manager với database
    conversation = ConversationManager()
    
    if not user_query:
        # Chế độ interactive (chạy standalone)
        print("=== 🚄 Hệ Thống Đặt Vé Tàu/Máy Bay ===")
        print("Tôi có thể giúp bạn:")
        print("• Đặt vé tàu/máy bay")
        print("• Hủy vé") 
        print("• Đổi giờ")
        print("• Xuất hóa đơn")
        print("• Khiếu nại")
        print("\nGõ 'exit' để thoát\n")
        
        # Hiển thị thông tin chuyến có sẵn
        print("📋 Các chuyến hiện có:")
        print("• Hà Nội → Sài Gòn: 08:00, 14:00")
        print("• Sài Gòn → Hà Nội: 09:00") 
        print("• Hà Nội → Đà Nẵng: 06:30, 15:45")
        print("-" * 50)
        
        while True:
            try:
                user_input = input("\n👤 Bạn: ").strip()
                
                if user_input.lower() in ['exit', 'quit', 'thoát']:
                    print("👋 Cảm ơn bạn đã sử dụng dịch vụ!")
                    break
                    
                if not user_input:
                    print("🤖 Bot: Vui lòng nhập câu hỏi của bạn.")
                    continue
                
                # Phân tích intent và entities
                signal = Signal(context=user_input)
                
                print(f"🔍 [Debug] Intent: {signal.intent}, Entities: {[e['entity'] + ':' + e['value'] for e in signal.entities]}")
                
                # Xử lý với conversation manager
                result = conversation.process_turn(user_input, signal.intent, signal.entities)
                
                # Hiển thị phản hồi
                print(f"🤖 Bot: {result['message']}")
                
                # Debug info chi tiết
                if result['status'] == 'need_more_info':
                    print(f"   📊 Đã thu thập: {result.get('collected', {})}")
                    print(f"   ❓ Còn thiếu: {result.get('missing', [])}")
                    
                    # Hiển thị các lựa chọn có sẵn nếu có
                    if 'available_options' in result:
                        print(f"   💡 Lựa chọn có sẵn: {result['available_options']}")
                        
                elif result['status'] == 'completed':
                    print(f"   ✅ Đã thực hiện: {result.get('executed_action', 'unknown')}")
                    
                    # Hiển thị thông tin đã lưu nếu là đặt vé
                    if result.get('executed_action') == 'dat_ve':
                        print("   💾 Thông tin vé đã được lưu để sử dụng cho các giao dịch tiếp theo")
                        
                elif result['status'] == 'failed':
                    print("   ❌ Giao dịch thất bại")
                    
                elif result['status'] == 'need_intent':
                    print("   🤔 Chưa xác định được ý định")
                    
            except KeyboardInterrupt:
                print("\n\n👋 Đã dừng chương trình!")
                break
            except Exception as e:
                print(f"❌ Lỗi: {str(e)}")
                print("Vui lòng thử lại!")
    else:
        # Chế độ API (được gọi từ controller)
        try:
            if not signal:
                signal = Signal(context=user_query)
            
            # Xử lý với conversation manager
            result = conversation.process_turn(user_query, signal.intent, signal.entities)
            
            return result['message']
            
        except Exception as e:
            print(f"❌ Lỗi L23: {str(e)}")
            return f"Xin lỗi, có lỗi xảy ra khi xử lý yêu cầu đặt vé. Vui lòng thử lại hoặc liên hệ tổng đài 1900 888 889."

def demo_conversation_flow():
    """Demo flow hội thoại mẫu"""
    print("\n" + "="*50)
    print("DEMO: Luồng hội thoại mẫu")
    print("="*50)
    
    conversation = ConversationManager()
    
    demo_inputs = [
        "Tôi muốn đặt vé từ Hà Nội đến Sài Gòn",
        "ngày mai", 
        "8h sáng",
        "2 vé",
        "Tôi muốn đổi giờ",
        "14:00",
        "Tôi muốn hủy vé"
    ]
    
    for i, user_input in enumerate(demo_inputs, 1):
        print(f"\n{i}. 👤 User: {user_input}")
        
        signal = Signal(context=user_input)
        result = conversation.process_turn(user_input, signal.intent, signal.entities)
        
        print(f"   🤖 Bot: {result['message']}")
        
        if result['status'] == 'completed':
            print(f"   ✅ Hoàn thành: {result.get('executed_action')}")

if __name__ == "__main__":
    # Chạy demo trước (tùy chọn)
    demo_mode = input("Bạn có muốn xem demo trước không? (y/n): ").lower()
    if demo_mode == 'y':
        demo_conversation_flow()
        input("\nNhấn Enter để tiếp tục chế độ thực...")
    
    # Chạy chương trình chính
    main()