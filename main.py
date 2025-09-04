#!/usr/bin/env python3
"""
Vexere Chatbot - Main Application
Ứng dụng chatbot hỗ trợ đặt vé xe và trả lời câu hỏi về chính sách
"""

import os
import sys
import uvicorn
import json
from fastapi import FastAPI, Request, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Import modules
try:
    from src.api.be import (
        handle_chat_request, 
        handle_websocket_message,
        get_system_stats,
        get_health_status,
        manager,
        ChatRequest
    )
    from src.database.kg_rag import policy_kg
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("🔧 Kiểm tra cấu trúc thư mục và các file __init__.py")
    sys.exit(1)

# Lifecycle management
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Khởi tạo và dọn dẹp ứng dụng"""
    print("🚀 Khởi động Vexere Chatbot...")
    
    # Initialize knowledge base
    try:
        print("📚 Đang khởi tạo knowledge base...")
        policy_kg()
        print("✅ Knowledge base đã được khởi tạo thành công")
    except Exception as e:
        print(f"⚠️ Lỗi khởi tạo knowledge base: {e}")
        print("🔄 Ứng dụng sẽ tiếp tục chạy nhưng có thể thiếu dữ liệu...")
    
    print("✅ Vexere Chatbot đã sẵn sàng!")
    
    yield
    
    print("🛑 Đang tắt Vexere Chatbot...")

# Create main FastAPI app
app = FastAPI(
    title="Vexere Chatbot",
    description="Chatbot hỗ trợ đặt vé xe và trả lời câu hỏi về chính sách",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files và frontend
if os.path.exists("frontend/static"):
    app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# API routes
@app.get("/", response_class=HTMLResponse)
async def home():
    """Trang chủ ứng dụng"""
    html_file = "frontend/index.html"
    if os.path.exists(html_file):
        with open(html_file, "r", encoding="utf-8") as f:
            return f.read()
    else:
        raise HTTPException(status_code=404, detail="Frontend not found")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return get_health_status()

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """
    Main chat endpoint - không yêu cầu API key
    """
    return await handle_chat_request(request)

@app.get("/stats")
async def get_stats():
    """Lấy thống kê hệ thống"""
    return get_system_stats()

# WebSocket endpoint
@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint cho real-time chat"""
    await manager.connect(websocket, session_id)
    try:
        while True:
            # Nhận tin nhắn từ client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            user_message = message_data.get("message", "")
            if not user_message:
                continue
            
            # Xử lý tin nhắn thông qua be.py
            await handle_websocket_message(websocket, session_id, user_message)
                
    except WebSocketDisconnect:
        manager.disconnect(session_id)
    except Exception as e:
        print(f"❌ WebSocket error for {session_id}: {e}")
        manager.disconnect(session_id)

# Main execution
if __name__ == "__main__":
    print("🚀 Khởi động Vexere Chatbot Server...")
    
    # Environment settings
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    debug = os.getenv("DEBUG", "true").lower() == "true"
    
    print(f"🌐 Server sẽ chạy tại: http://{host}:{port}")
    print(f"📚 API Documentation: http://{host}:{port}/docs")
    print(f"🔧 Debug mode: {debug}")
    print("🎯 Chế độ: Miễn phí (không cần API key)")
    
    # Chạy server
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug,
        access_log=True,
        log_level="info" if not debug else "debug"
    )