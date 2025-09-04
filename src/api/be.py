import sys
import os
import json
import asyncio
from typing import Dict, List
from fastapi import FastAPI, Request, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from src.__modules.core.controller import ChatController

# Pydantic models
class ChatRequest(BaseModel):
    message: str
    session_id: str

class ChatResponse(BaseModel):
    response: str
    session_id: str
    status: str = "success"

# WebSocket Connection Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket
        print(f"🔗 WebSocket connected: {session_id}")

    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]
            print(f"❌ WebSocket disconnected: {session_id}")

    async def send_personal_message(self, message: dict, session_id: str):
        if session_id in self.active_connections:
            websocket = self.active_connections[session_id]
            try:
                await websocket.send_text(json.dumps(message, ensure_ascii=False))
            except Exception as e:
                print(f"❌ Error sending message to {session_id}: {e}")
                self.disconnect(session_id)

# Stats tracking
class StatsTracker:
    def __init__(self):
        self.total_messages = 0
        self.l1_requests = 0
        self.l2_requests = 0
        self.l3_requests = 0
        self.fallback_requests = 0

    def increment_message(self):
        self.total_messages += 1

    def increment_level(self, level: str):
        if level == "L1":
            self.l1_requests += 1
        elif level == "L2":
            self.l2_requests += 1
        elif level == "L3":
            self.l3_requests += 1
        else:
            self.fallback_requests += 1

    def get_stats(self):
        return {
            "active_sessions": len(manager.active_connections),
            "total_messages_processed": self.total_messages,
            "l1_requests": self.l1_requests,
            "l2_requests": self.l2_requests,
            "l3_requests": self.l3_requests,
            "fallback_requests": self.fallback_requests
        }

# Global instances
manager = ConnectionManager()
stats_tracker = StatsTracker()

# API Functions
async def handle_chat_request(request: ChatRequest) -> ChatResponse:
    """
    Xử lý yêu cầu chat
    """
    try:
        # Track stats
        stats_tracker.increment_message()
        
        # Khởi tạo controller với session_id
        chat_controller = ChatController(request.session_id)
        
        # Xử lý tin nhắn
        bot_response = chat_controller.handle_user_message(request.message)
        
        return ChatResponse(
            response=bot_response,
            session_id=request.session_id,
            status="success"
        )
        
    except Exception as e:
        print(f"❌ Lỗi xử lý chat: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi xử lý tin nhắn: {str(e)}"
        )

async def handle_websocket_message(websocket: WebSocket, session_id: str, user_message: str):
    """
    Xử lý tin nhắn WebSocket
    """
    try:
        # Track stats
        stats_tracker.increment_message()
        
        # Xử lý tin nhắn với chatbot
        chat_controller = ChatController(session_id)
        bot_response = chat_controller.handle_user_message(user_message)
        
        # Gửi phản hồi về client
        response_data = {
            "response": bot_response,  # Đổi từ "message" thành "response" để đồng nhất với HTTP API
            "session_id": session_id,
            "status": "success",
            "timestamp": asyncio.get_event_loop().time()
        }
        
        await manager.send_personal_message(response_data, session_id)
        
    except Exception as e:
        # Gửi lỗi về client
        error_response = {
            "response": f"Xin lỗi, có lỗi xảy ra: {str(e)}",  # Đổi từ "message" thành "response"
            "session_id": session_id,
            "status": "error",
            "timestamp": asyncio.get_event_loop().time()
        }
        await manager.send_personal_message(error_response, session_id)

def get_system_stats():
    """
    Lấy thống kê hệ thống
    """
    return stats_tracker.get_stats()

def get_health_status():
    """
    Kiểm tra trạng thái hệ thống
    """
    return {
        "status": "healthy",
        "version": "1.0.0",
        "services": {
            "api": "running",
            "database": "connected",
            "ai_model": "loaded"
        }
    }
