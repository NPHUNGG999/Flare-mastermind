"""
============================================
 FLARE AI - Main Entry Point
============================================
File chính khởi động toàn bộ bot
============================================
"""

import sys
from pathlib import Path

from .utils.config import config
from .utils.logger import setup_logger, get_logger
from .bot.client import FlareBot
from .bot.events import setup_events

# Setup logger
logger = setup_logger(log_level=config.bot.log_level)
log = get_logger(__name__)

def main():
    """
    Hàm chính khởi động FLARE AI Bot
    
    Flow:
    1. Kiểm tra cấu hình
    2. Tạo bot instance
    3. Setup events
    4. Chạy bot
    """
    
    # 1. Kiểm tra cấu hình
    log.info("🔍 Đang kiểm tra cấu hình...")
    if not config.validate():
        log.error("❌ Cấu hình không hợp lệ!")
        sys.exit(1)
    
    log.info("✅ Cấu hình hợp lệ!")
    
    # 2. Tạo bot instance
    log.info(f"🤖 Đang khởi tạo {config.bot.name}...")
    bot = FlareBot()
    
    # 3. Setup events
    log.info("📡 Đang thiết lập event handlers...")
    setup_events(bot)
    
    # 4. Chạy bot
    log.info(f"🚀 Đang khởi động {config.bot.name}...")
    
    try:
        bot.run_bot()
    except KeyboardInterrupt:
        log.info("👋 Bot đã được tắt an toàn!")
    except Exception as e:
        log.exception(f"❌ Lỗi nghiêm trọng: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
