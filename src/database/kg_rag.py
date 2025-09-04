import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from config.settings import config
import re
import json

# Sử dụng đường dẫn tương đối từ thư mục gốc
document_text_path = "src/database/docs/vexere_policy_structured.txt"
faq_data_path = "src/database/docs/vexere_support_data.json"

def create_semantic_chunks(text):
    """
    Hàm này chia văn bản thành các đoạn (chunks) dựa trên các tiêu đề (##).
    Mỗi chunk sẽ chứa nội dung dưới một tiêu đề và metadata là chính tiêu đề đó.
    """
    parts = re.split(r'(## .*)', text)
    chunks = []
    metadatas = []
    current_heading = "Giới thiệu chung"

    if parts[0].strip() == "":
        parts = parts[1:]

    for i in range(len(parts)):
        part = parts[i].strip()
        if part.startswith("##"):
            current_heading = part.replace("##", "").strip()
        elif part:
            cleaned_text = re.sub(r'📄', '', part).strip()
            cleaned_text = re.sub(r'\s{2,}', ' ', cleaned_text)
            chunks.append(cleaned_text)
            metadatas.append({"source": current_heading})
            
    return chunks, metadatas

def policy_kg():
    """Khởi tạo knowledge graph từ file policy"""
    if not os.path.exists(document_text_path):
        print(f"File không tồn tại: {document_text_path}")
        return
        
    with open(document_text_path, "r", encoding="utf-8") as file:
        document_text = file.read()

    chunks, metadatas = create_semantic_chunks(document_text)

    print(f"Đã tạo ra {len(chunks)} đoạn văn bản (chunks).")

    print("\nĐang tải mô hình embedding 'Alibaba-NLP/gte-multilingual-base'...")
    # LƯU Ý: Lần đầu tiên chạy, quá trình tải mô hình này có thể mất vài phút.
    # trust_remote_code=True là bắt buộc để mô hình này hoạt động.
    model = config.model
    print("Mô hình đã được tải.")

    # Tạo embeddings cho tất cả các chunks
    print("Đang tạo embeddings cho các chunks...")
    embeddings = model.encode(chunks, show_progress_bar=True)
    print(f"Đã tạo xong {len(embeddings)} embeddings.")

    ids = [f"chunk_{i}" for i in range(len(chunks))]

    # Thêm dữ liệu vào collection
    config.collection.add(
        embeddings=embeddings,
        documents=chunks,
        metadatas=metadatas,
        ids=ids
    )

    print(f"Đã thêm thành công {config.collection.count()} tài liệu vào ChromaDB.")

def faq_kg():
    """Tải FAQ knowledge graph"""
    if not os.path.exists(faq_data_path):
        print(f"File FAQ không tồn tại: {faq_data_path}")
        return {}
        
    with open(faq_data_path, "r", encoding="utf-8") as file:
        faq_data = json.load(file)
    
    # Lọc ra các FAQ có content
    faq_data = {
        key: value for key, value in faq_data.items() 
        if value.get('content') and len(value['content']) > 0
    }

    return faq_data