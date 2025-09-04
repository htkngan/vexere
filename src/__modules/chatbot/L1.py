import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import re
import os
import sys
import dotenv
from google import genai
import fuzzywuzzy
from fuzzywuzzy import process

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, project_root)

from config.settings import config
from src.database.kg_rag import faq_kg, policy_kg

dotenv.load_dotenv()

def bot_response(query_text):
    # Khởi tạo faq_kg
    faq_data = faq_kg()
    faq_questions = list(faq_data.keys())
    
    best_match, score = process.extractOne(query_text, faq_questions)
    if score >= 90:
        content = faq_data[best_match]['content']
        if isinstance(content, list):
            return "\n".join(content)
        return content
    else:
    

        # 1. Chuyển câu hỏi thành vector
        query_embedding = config.model.encode(query_text)

        # 2. Truy vấn trong collection
        results = config.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=3
        )
        context = "\n".join(results['documents'][0])

        prompt = f"""
        Bạn là một trợ lý AI giúp hệ thống giải thích về chính sách, quy định, thủ tục và các thao tác có trong {context}
        Câu hỏi của khách hàng: {query_text}
        Bạn có thể thân thiện chào hỏi. Hỏi khách hàng thêm thông tin nếu cần.
        Hãy trả lời câu hỏi dựa trên ngữ cảnh ở trên. Nếu không tìm thấy thông tin liên quan, hãy trả lời rằng bạn không biết.
        """

        try:
            if config.agent:
                response = config.agent.models.generate_content(
                    model = "gemini-2.0-flash",
                    contents = prompt
                )
                return response.text
            else:
                # Không có API key, sử dụng fallback
                raise Exception("API key không khả dụng")
        except Exception as e:
            print(f"⚠️ Lỗi API Gemini: {e}")

if __name__ == "__main__":
    print("Hệ thống đã sẵn sàng để trả lời câu hỏi.")
    while True:
        user_query = input("\nNhập câu hỏi của bạn (hoặc 'exit' để thoát): ")
        if user_query.lower() == 'exit':
            break
        response = bot_response(user_query)
        print(f"Trả lời: {response}")
