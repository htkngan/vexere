# 🚄 Vexere Chatbot

Hệ thống chatbot thông minh hỗ trợ đặt vé xe và trả lời câu hỏi về chính sách vé xe.

## ✨ Tính năng

- **🎫 Đặt vé thông minh**: Hỗ trợ đặt vé xe với AI hiểu ngữ cảnh
- **📋 FAQ & Chính sách**: Trả lời câu hỏi về chính sách, quy định
- **🔄 Quản lý vé**: Hủy, đổi giờ, xuất hóa đơn
- **💬 Chat UI**: Giao diện chat hiện đại với hỗ trợ giọng nói
- **🎯 Miễn phí**: Không cần API key hay đăng ký

## 🏗️ Kiến trúc hệ thống

```
├── L1: FAQ & Policy (ChromaDB + Fuzzy Search)
├── L23: Booking & After-service (NLP + Conversation Manager)
└── Router: AI-based intent classification
```

## 🚀 Cài đặt và Deploy

### 1. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 2. Cấu hình môi trường (tùy chọn)

**💡 Tùy chọn**: Để có trải nghiệm tốt nhất với AI, bạn có thể cấu hình Google API key.

Cập nhật file `.env`:

```env
# Lấy API key miễn phí tại: https://aistudio.google.com/app/apikey
GOOGLE_API_KEY=your_google_ai_api_key_here
REDIS_URL=redis://localhost:6379/0
```

**🔑 Cách lấy Google AI API Key:**
1. Truy cập: https://aistudio.google.com/app/apikey
2. Đăng nhập với tài khoản Google
3. Tạo API key mới
4. Copy và dán vào file `.env`

**📝 Lưu ý**: Nếu không có API key, hệ thống vẫn hoạt động với khả năng fallback.

### 3. Khởi động Redis (tùy chọn)

```bash
# Với Docker
docker run -d -p 6379:6379 redis:alpine

# Hoặc cài đặt local
brew install redis  # macOS
redis-server
```

### 4. Chạy ứng dụng

```bash
python main.py
```

Server sẽ chạy tại: `http://localhost:8000`

## 📡 API Documentation

### Endpoints

- `GET /` - Trang chủ web interface
- `POST /chat` - Chat với bot (yêu cầu API key)
- `GET /docs` - Swagger documentation
- `GET /health` - Health check

### Sử dụng API

```bash
curl -X POST "http://localhost:8000/chat" \
  -H "x-api-key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Tôi muốn đặt vé từ Hà Nội đi Sài Gòn",
    "session_id": "user_123"
  }'
```

## 🛠️ Cấu trúc dự án

```
vexere/
├── main.py                      # Entry point
├── config/
│   └── settings.py             # Cấu hình chung
├── src/
│   ├── api/
│   │   └── be.py               # FastAPI routes
│   ├── __modules/
│   │   ├── core/
│   │   │   ├── controller.py   # Chat controller
│   │   │   └── conversation_manager.py  # Memory management
│   │   ├── chatbot/
│   │   │   ├── L1.py          # FAQ & Policy layer
│   │   │   ├── L23.py         # Booking layer
│   │   │   └── nlp_extractor/
│   │   │       └── nlp_engine.py  # NLP processing
│   │   └── nlp/
│   │       └── threading.py    # Intent routing
│   └── database/
│       ├── schemas.py          # Database models
│       ├── kg_rag.py          # Knowledge graph
│       └── docs/              # Documentation files
└── frontend/
    ├── index.html             # Web interface
    └── static/
        ├── app.js             # Frontend JavaScript
        └── styles.css         # CSS styles
```

## 🔧 Cấu hình

### Google AI API

1. Truy cập [Google AI Studio](https://aistudio.google.com/)
2. Tạo API key
3. Thêm vào file `.env`

### Redis (tùy chọn)

Nếu không có Redis, hệ thống sẽ sử dụng memory storage.

## 📊 Monitoring

Truy cập `/stats` để xem thống kê hệ thống.

## 🐛 Debug

Bật debug mode trong `.env`:

```env
DEBUG=true
```

## 🚀 Production Deployment

### Docker

```bash
# Build image
docker build -t vexere-chatbot .

# Run container
docker run -p 8000:8000 --env-file .env vexere-chatbot
```

### Systemd (Linux)

Tạo file `/etc/systemd/system/vexere-chatbot.service`:

```ini
[Unit]
Description=Vexere Chatbot
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/vexere
Environment=PATH=/path/to/venv/bin
ExecStart=/path/to/venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable vexere-chatbot
sudo systemctl start vexere-chatbot
```

## 📝 Logs

Logs được ghi tại:
- Console output
- Uvicorn access logs
- Application errors
