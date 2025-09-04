#!/usr/bin/env python3
"""
Test script cho flow conversation liên tục
"""
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.__modules.core.controller import ChatController

def test_continuous_flow():
    """Test flow liên tục cho đặt vé"""
    print("=== TEST FLOW LIÊN TỤC ===")
    
    # Tạo controller với session_id
    controller = ChatController("test_session_001")
    
    # Test case: Đặt vé liên tục
    test_messages = [
        "Tôi muốn đặt vé",
        "Hà Nội", 
        "Sài Gòn",
        "ngày mai",
        "2 vé",
        "9h"
    ]
    
    print("\n🔥 Test case: Đặt vé liên tục")
    print("Expecting: Bot sẽ duy trì conversation cho đến khi hoàn thành đặt vé")
    print("-" * 60)
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n{i}. 👤 User: {message}")
        
        # Kiểm tra trạng thái conversation
        status = controller.get_conversation_status()
        if status:
            print(f"   📊 Trạng thái: Intent={status['current_intent']}, Entities={len(status['collected_entities'])}")
        
        # Gửi message
        response = controller.handle_user_message(message)
        print(f"   🤖 Bot: {response}")
        
        # Kiểm tra có đang trong flow không
        in_flow = controller.is_in_conversation_flow()
        print(f"   🔄 Đang trong flow: {in_flow}")
    
    print("\n" + "="*60)
    
    # Test case: Hủy flow giữa chừng
    print("\n🔥 Test case: Hủy flow giữa chừng")
    print("Expecting: User có thể hủy flow và bắt đầu lại")
    print("-" * 60)
    
    controller2 = ChatController("test_session_002")
    
    test_messages_2 = [
        "Tôi muốn đặt vé",
        "Hà Nội",
        "hủy",  # Hủy giữa chừng
        "Tôi muốn đặt vé từ Sài Gòn đến Hà Nội",
        "mai",
        "1 vé",
        "9h"
    ]
    
    for i, message in enumerate(test_messages_2, 1):
        print(f"\n{i}. 👤 User: {message}")
        
        status = controller2.get_conversation_status()
        if status:
            print(f"   📊 Trạng thái: Intent={status['current_intent']}, Entities={len(status['collected_entities'])}")
        
        response = controller2.handle_user_message(message)
        print(f"   🤖 Bot: {response}")
        
        in_flow = controller2.is_in_conversation_flow()
        print(f"   🔄 Đang trong flow: {in_flow}")
    
    print("\n" + "="*60)
    
    # Test case: Đặt vé rồi đổi giờ liên tục  
    print("\n🔥 Test case: Đặt vé -> Đổi giờ liên tục")
    print("Expecting: Sau khi đặt vé thành công, có thể đổi giờ ngay với mã vé vừa tạo")
    print("-" * 60)
    
    controller3 = ChatController("test_session_003")
    
    test_messages_3 = [
        "Đặt vé từ Hà Nội đến Sài Gòn",
        "mai", 
        "1 vé",
        "8h",
        "Tôi muốn đổi giờ",  # Ngay sau khi đặt vé
        "14:00"
    ]
    
    for i, message in enumerate(test_messages_3, 1):
        print(f"\n{i}. 👤 User: {message}")
        
        status = controller3.get_conversation_status()
        if status:
            print(f"   📊 Trạng thái: Intent={status['current_intent']}, Entities={len(status['collected_entities'])}")
        
        response = controller3.handle_user_message(message)
        print(f"   🤖 Bot: {response}")
        
        in_flow = controller3.is_in_conversation_flow()
        print(f"   🔄 Đang trong flow: {in_flow}")
    
    print("\n✅ Hoàn thành test!")

if __name__ == "__main__":
    test_continuous_flow()
