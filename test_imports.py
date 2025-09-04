#!/usr/bin/env python3
"""
Test script để kiểm tra tất cả imports
"""

import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_imports():
    """Test tất cả imports quan trọng"""
    print("🔍 Testing imports...")
    
    try:
        print("✓ Testing config.settings...")
        from config.settings import config
        print(f"  - Config loaded: {type(config)}")
        
        print("✓ Testing src.database.kg_rag...")
        from src.database.kg_rag import policy_kg, faq_kg
        print("  - KG modules loaded")
        
        print("✓ Testing src.database.schemas...")
        from src.database.schemas import db
        print("  - Database schemas loaded")
        
        print("✓ Testing src.__modules.core.conversation_manager...")
        from src.__modules.core.conversation_manager import ChatMemory
        print("  - Conversation manager loaded")
        
        print("✓ Testing src.__modules.core.controller...")
        from src.__modules.core.controller import ChatController
        print("  - Chat controller loaded")
        
        print("✓ Testing src.__modules.nlp.threading...")
        from src.__modules.nlp.threading import threaded_main
        print("  - NLP threading loaded")
        
        print("✓ Testing src.__modules.chatbot.L1...")
        from src.__modules.chatbot.L1 import bot_response
        print("  - L1 bot loaded")
        
        print("✓ Testing src.__modules.chatbot.L23...")
        from src.__modules.chatbot.L23 import Signal, main
        print("  - L23 bot loaded")
        
        print("✓ Testing src.api.be...")
        from src.api.be import verify_api_key
        print("  - API module loaded")
        
        print("\n🎉 All imports successful!")
        return True
        
    except ImportError as e:
        print(f"\n❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Vexere Chatbot - Import Test")
    print("=" * 50)
    
    success = test_imports()
    
    if success:
        print("\n✅ Ready to run main.py!")
        print("Run: python main.py")
    else:
        print("\n❌ Fix import errors before running main.py")
        sys.exit(1)
