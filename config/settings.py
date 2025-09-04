import os
import dotenv
from google import genai
from google.genai import types
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

dotenv.load_dotenv()

class Config:
    # Kiểm tra API key trước khi khởi tạo client
    google_api_key = os.getenv("GOOGLE_API_KEY")
    
    if google_api_key and google_api_key.strip() and google_api_key != "your-api-key-here":
        try:
            agent = genai.Client(api_key=google_api_key)
            print("✅ Gemini API đã được khởi tạo thành công")
        except Exception as e:
            print(f"⚠️ Lỗi khởi tạo Gemini API: {e}")
            print("🔄 Hệ thống sẽ chạy ở chế độ fallback")
            agent = None
    else:
        print("⚠️ Không tìm thấy Google API key hợp lệ")
        print("🔄 Hệ thống sẽ chạy ở chế độ fallback")
        agent = None

    client = chromadb.Client(
    Settings(
        anonymized_telemetry=False,
        allow_reset=True
    )
)
    collection_name = "vexere_policy_gte"
    collection = client.get_or_create_collection(name=collection_name)
    model = SentenceTransformer(
        'Alibaba-NLP/gte-multilingual-base', 
        trust_remote_code=True
    )

    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    API_KEY = os.getenv("API_KEYS", "test-key").split(",")
    API_KEY_NAME = "x-api-key"



config = Config()