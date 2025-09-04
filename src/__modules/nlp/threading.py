import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, project_root)

from config.settings import config

def threaded_main(user_query: str):
    prompt = f"""Tự động phân tích câu hỏi của người dùng và chuyển đến mô-đun phù hợp:
    - Nếu câu hỏi liên quan đến chính sách, quy định, thủ tục, hoàn tiền -> Chuyển đến mô-đun L1
    - Nếu câu hỏi liên quan đến đặt vé, hủy vé, đổi giờ, xuất hóa đơn, khiếu nại -> Chuyển đến mô-đun L23

    Câu hỏi: {user_query}
    Kết quả trả về: "L1" hoặc "L23"
    Không giải thích gì thêm, chỉ trả về "L1" hoặc "L23".
    """

    result = config.agent.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )
    return result.text.strip()