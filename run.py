#!/usr/bin/env python3
"""
============================================
 FLARE AI Discord Bot - Launcher
============================================
Chạy file này để khởi động bot
Cách dùng: python run.py
============================================
"""

import sys
import os
from pathlib import Path

# Thêm thư mục src vào PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent / "src"))

def print_banner():
    """In banner khởi động"""
    banner = """
    ╔══════════════════════════════════════╗
    ║          🚀 FLARE AI BOT           ║
    ║       Starting up system...        ║
    ║       Please wait a moment         ║
    ╚══════════════════════════════════════╝
    """
    print(banner)

def check_environment():
    """Kiểm tra môi trường trước khi chạy"""
    from pathlib import Path
    
    # Kiểm tra file .env
    if not Path(".env").exists():
        print("❌ Không tìm thấy file .env!")
        print("👉 Hãy copy .env.example thành .env và điền thông tin:")
        print("   cp .env.example .env")
        return False
    
    # Kiểm tra các thư mục cần thiết
    required_dirs = ["logs", "data", "config"]
    for dir_name in required_dirs:
        Path(dir_name).mkdir(parents=True, exist_ok=True)
    
    return True

def main():
    """Hàm chính khởi động bot"""
    try:
        # In banner
        print_banner()
        
        # Kiểm tra môi trường
        if not check_environment():
            sys.exit(1)
        
        # Import và chạy bot
        from src.main import main as start_bot
        start_bot()
        
    except KeyboardInterrupt:
        print("\n\n👋 FLARE AI đã được tắt an toàn!")
        sys.exit(0)
        
    except ImportError as e:
        print(f"\n❌ Lỗi import: {e}")
        print("👉 Hãy cài đặt dependencies: pip install -r requirements.txt")
        sys.exit(1)
        
    except Exception as e:
        print(f"\n❌ Lỗi không xác định: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
