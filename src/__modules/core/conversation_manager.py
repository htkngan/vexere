import json
import redis
from datetime import datetime, timezone
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, project_root)

from config.settings import Config

try:
    redis_client = redis.Redis.from_url(Config.REDIS_URL)
    redis_client.ping()
    print("Successfully connected to Redis for chat memory.")
except redis.exceptions.ConnectionError as e:
    print(f"Could not connect to Redis: {e}")
    redis_client = None

class RedisMemoryStore:
    """
    Lớp cấp thấp, tương tác trực tiếp với Redis để lưu/tải/xóa dữ liệu của một session.
    """
    def __init__(self, session_id: str):
        if not redis_client:
            raise ConnectionError("Redis client is not available.")
        self.session_id = session_id

    def load(self) -> list:
        """Tải lịch sử hội thoại từ Redis."""
        raw = redis_client.get(self.session_id)
        if raw:
            return json.loads(raw)
        return []

    def save(self, memory: list):
        """Lưu lịch sử hội thoại vào Redis với TTL là 1 giờ."""
        redis_client.set(self.session_id, json.dumps(memory, ensure_ascii=False), ex=3600)

    def clear(self):
        """Xóa lịch sử hội thoại của session."""
        redis_client.delete(self.session_id)


class ChatMemory:
    """
    Lớp cấp cao, cung cấp các phương thức để quản lý bộ nhớ hội thoại.
    Tương ứng với component: Catching memory
    """
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.redis_store = RedisMemoryStore(session_id)
    
    def add_message(self, role: str, message: str):
        """Thêm một tin nhắn (từ user hoặc bot) vào lịch sử."""
        history = self.redis_store.load()
        history.append({
            "role": role,
            "message": message,
            # Sử dụng datetime thay cho pandas để nhẹ hơn
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        self.redis_store.save(history)
    
    def get_history(self) -> list:
        """Lấy toàn bộ lịch sử hội thoại."""
        return self.redis_store.load()

    def format_history_for_context(self, max_messages: int = 10) -> str:
        """
        Định dạng một phần lịch sử gần đây để làm ngữ cảnh cho các mô hình AI.
        """
        history = self.redis_store.load()
        # Lấy `max_messages` tin nhắn cuối cùng
        recent_history = history[-max_messages:]
        
        # Định dạng lại thành một chuỗi dễ đọc
        formatted_lines = []
        for m in recent_history:
            # Xác định người nói
            speaker = "Người dùng" if m['role'] == 'user' else "Bot"
            formatted_lines.append(f"{speaker}: {m['message']}")
            
        return "\n".join(formatted_lines)

    def clear_history(self):
        """Xóa trắng lịch sử của session."""
        self.redis_store.clear()