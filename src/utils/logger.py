"""
============================================
 FLARE AI - Advanced Logging System
============================================
Hệ thống log chuyên nghiệp cho bot
============================================
"""

import sys
from pathlib import Path
from loguru import logger
from typing import Optional

def setup_logger(
    log_level: str = "INFO",
    log_file: Optional[str] = "logs/flare_ai.log"
) -> logger:
    """
    Thiết lập hệ thống logging
    
    Args:
        log_level: Mức độ log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Đường dẫn file log
    
    Returns:
        Logger đã được cấu hình
    """
    
    # Xóa handler mặc định
    logger.remove()
    
    # Handler cho console (có màu sắc)
    logger.add(
        sys.stdout,
        format=(
            "<green>{time:HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>"
        ),
        level=log_level,
        colorize=True
    )
    
    # Handler cho file (lưu trữ lâu dài)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.add(
            str(log_path),
            format=(
                "{time:YYYY-MM-DD HH:mm:ss} | "
                "{level: <8} | "
                "{name}:{function}:{line} - "
                "{message}"
            ),
            level=log_level,
            rotation="10 MB",      # Tạo file mới khi đạt 10MB
            retention="7 days",    # Giữ log 7 ngày
            compression="zip"      # Nén file log cũ
        )
    
    return logger

def get_logger(name: str = "FLARE_AI") -> logger:
    """
    Lấy logger với tên cụ thể
    
    Args:
        name: Tên logger
    
    Returns:
        Logger instance
    """
    return logger.bind(name=name)

# Logger mặc định
log = get_logger()
