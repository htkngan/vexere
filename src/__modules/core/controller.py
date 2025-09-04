import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, project_root)

# Controller for get and post requests
from src.__modules.chatbot.L23 import main, Signal
from src.__modules.chatbot.L1 import bot_response
from src.__modules.core.conversation_manager import ChatMemory
from src.__modules.nlp.threading import threaded_main
from src.database.schemas import db

# Global ticket tracking để chia sẻ giữa sessions
class GlobalTicketManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GlobalTicketManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.recent_tickets = {}  # session_id -> ticket_info
    
    def store_ticket(self, session_id, ticket_info):
        """Lưu thông tin vé cho session"""
        self.recent_tickets[session_id] = ticket_info
    
    def get_ticket(self, session_id):
        """Lấy thông tin vé của session"""
        return self.recent_tickets.get(session_id)

global_ticket_manager = GlobalTicketManager()

class ChatController:
    def __init__(self, session_id):
        self.session_id = session_id
        self.session = ChatMemory(session_id)
        self.action = None
        # Quản lý conversation cho L23
        self.conversation_manager = None

    def handle_user_message(self, user_message: str) -> str:
        # Lưu tin nhắn của user
        self.session.add_message("user", user_message)
        
        try:
            # Kiểm tra lệnh hủy flow
            if user_message.lower().strip() in ['hủy', 'cancel', 'dừng', 'stop', 'thoát flow', 'reset']:
                if self.conversation_manager:
                    self.conversation_manager = None
                    response = "✅ Đã hủy giao dịch hiện tại. Bạn có thể bắt đầu lại hoặc hỏi tôi điều gì khác."
                    self.session.add_message("bot", response)
                    return response
            
            # Kiểm tra nếu đang trong conversation flow thì ưu tiên L23
            if self.is_in_conversation_flow():
                # Đang trong flow đặt vé, tiếp tục xử lý ở L23
                
                # Inject ticket info từ global manager nếu có
                recent_ticket = global_ticket_manager.get_ticket(self.session_id)
                if recent_ticket and 'dat_ve' not in self.conversation_manager.state.completed_actions:
                    self.conversation_manager.state.completed_actions['dat_ve'] = recent_ticket
                
                signal = Signal(context=user_message)
                
                print(f"🔄 [Tiếp tục flow] Intent: {signal.intent}, Entities: {[e['entity'] + ':' + e['value'] for e in signal.entities]}")
        
                # Xử lý với conversation manager đã lưu trạng thái
                result = self.conversation_manager.process_turn(user_message, signal.intent, signal.entities)
                
                # Kiểm tra nếu action đã hoàn thành thì reset conversation manager
                if result['status'] == 'completed':
                    print(f"   ✅ Hoàn thành: {result.get('executed_action')}")
                    
                    # Lưu thông tin vé nếu là đặt vé thành công  
                    if result.get('executed_action') == 'dat_ve':
                        ticket_info = self.conversation_manager.state.completed_actions.get('dat_ve')
                        print(f"   🔍 [Tiếp tục] Ticket info: {ticket_info}")
                        if ticket_info:
                            global_ticket_manager.store_ticket(self.session_id, ticket_info)
                            print(f"   💾 [Tiếp tục] Đã lưu mã vé {ticket_info['ticket_code']} cho session {self.session_id}")
                    
                    # Reset conversation manager sau khi hoàn thành action
                    self.conversation_manager = None
                elif result['status'] == 'failed':
                    print("   ❌ Giao dịch thất bại")
                    # Reset conversation manager khi thất bại
                    self.conversation_manager = None
                
                response = result['message']
                self.session.add_message("bot", response)
                return response
            
            # Phân tích xem nên chuyển đến L1 hay L23
            self.action = threaded_main(user_message)
            
            if self.action and self.action.strip():
                if "L1" in self.action:
                    response = bot_response(user_message)
                    self.session.add_message("bot", response)
                    return response
                elif "L23" in self.action:
                    # Khởi tạo conversation manager nếu chưa có
                    if not self.conversation_manager:
                        from src.__modules.chatbot.nlp_extractor.nlp_engine import ConversationManager
                        self.conversation_manager = ConversationManager()
                        
                        # Nếu có database từ conversation manager trước đó thì sử dụng lại
                        # (Database đã là singleton nên sẽ tự động chia sẻ)
                        
                        # Inject ticket info từ global manager nếu có
                        recent_ticket = global_ticket_manager.get_ticket(self.session_id)
                        if recent_ticket:
                            self.conversation_manager.state.completed_actions['dat_ve'] = recent_ticket
                            print(f"   🔗 Đã inject mã vé: {recent_ticket['ticket_code']}")
                    
                    # Phân tích intent và entities
                    signal = Signal(context=user_message)
                    
                    print(f"🔍 [Debug] Intent: {signal.intent}, Entities: {[e['entity'] + ':' + e['value'] for e in signal.entities]}")
            
                    # Xử lý với conversation manager đã lưu trạng thái
                    result = self.conversation_manager.process_turn(user_message, signal.intent, signal.entities)
                         # Kiểm tra nếu action đã hoàn thành thì reset conversation manager
                if result['status'] == 'completed':
                    print(f"   ✅ Hoàn thành: {result.get('executed_action')}")
                    
                    # Lưu thông tin vé nếu là đặt vé thành công
                    if result.get('executed_action') == 'dat_ve':
                        ticket_info = self.conversation_manager.state.completed_actions.get('dat_ve')
                        print(f"   🔍 Ticket info: {ticket_info}")
                        if ticket_info:
                            global_ticket_manager.store_ticket(self.session_id, ticket_info)
                            print(f"   💾 Đã lưu mã vé {ticket_info['ticket_code']} cho session {self.session_id}")
                    
                    # Reset conversation manager sau khi hoàn thành action
                    self.conversation_manager = None
                elif result['status'] == 'failed':
                    print("   ❌ Giao dịch thất bại")
                    # Reset conversation manager khi thất bại
                    self.conversation_manager = None
                    
                    response = result['message']
                    
                    # Lưu tin nhắn của bot
                    self.session.add_message("bot", response)
                    return response
        except Exception as e:
            print(f"❌ Lỗi trong controller: {str(e)}")
        
        # Fallback
        response = "Xin lỗi, tôi không hiểu câu hỏi của bạn. Bạn có thể hỏi về chính sách vé xe hoặc đặt vé không?"
        self.session.add_message("bot", response)
        return response
    
    def reset_conversation(self):
        """Reset conversation manager khi cần bắt đầu lại"""
        self.conversation_manager = None
        
    def get_conversation_status(self):
        """Kiểm tra trạng thái conversation"""
        if not self.conversation_manager:
            return None
        return {
            'current_intent': self.conversation_manager.state.current_intent,
            'collected_entities': self.conversation_manager.state.collected_entities,
            'completed_actions': self.conversation_manager.state.completed_actions
        }
        
    def is_in_conversation_flow(self):
        """Kiểm tra có đang trong flow conversation không"""
        return self.conversation_manager is not None and self.conversation_manager.state.current_intent is not None
