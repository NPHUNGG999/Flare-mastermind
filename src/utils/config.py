"""
============================================
 FLARE AI - Configuration Manager
============================================
Quản lý tất cả cấu hình của bot
============================================
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from dotenv import load_dotenv
import yaml

# Load biến môi trường
load_dotenv()

@dataclass
class DiscordConfig:
    """Cấu hình Discord"""
    token: str = field(default_factory=lambda: os.getenv("DISCORD_TOKEN", ""))
    prefix: str = field(default_factory=lambda: os.getenv("DISCORD_PREFIX", "!"))
    owner_id: Optional[int] = field(
        default_factory=lambda: int(os.getenv("DISCORD_OWNER_ID", "0")) or None
    )

@dataclass
class GeminiConfig:
    """Cấu hình Google Gemini API - TIẾT KIỆM QUOTA"""
    api_key: str = field(default_factory=lambda: os.getenv("GEMINI_API_KEY", ""))
    model: str = field(
        default_factory=lambda: os.getenv("GEMINI_MODEL", "models/gemini-3.1-flash-lite-preview")
    )
    temperature: float = field(
        default_factory=lambda: float(os.getenv("GEMINI_TEMPERATURE", "0.7"))
    )
    # GIỚI HẠN MAX TOKENS = 250 ĐỂ TIẾT KIỆM QUOTA
    max_tokens: int = field(
        default_factory=lambda: int(os.getenv("GEMINI_MAX_TOKENS", "250"))
    )
    # Giới hạn request mỗi phút
    max_requests_per_minute: int = 10

@dataclass
class BotConfig:
    """Cấu hình Bot"""
    name: str = field(default_factory=lambda: os.getenv("BOT_NAME", "FLARE AI"))
    color: int = field(
        default_factory=lambda: int(os.getenv("BOT_COLOR", "0x00ffcc"), 16)
    )
    log_level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))
    # Giảm lịch sử xuống 5 cặp để tiết kiệm token
    max_history: int = field(
        default_factory=lambda: int(os.getenv("MAX_HISTORY", "10"))
    )

@dataclass
class Config:
    """Class cấu hình tổng"""
    discord: DiscordConfig = field(default_factory=DiscordConfig)
    gemini: GeminiConfig = field(default_factory=GeminiConfig)
    bot: BotConfig = field(default_factory=BotConfig)
    prompts: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def load(cls) -> "Config":
        """Load tất cả cấu hình"""
        config = cls()
        
        # Load prompts từ file YAML
        prompts_dir = Path("config")
        if prompts_dir.exists():
            for yaml_file in prompts_dir.glob("*.yaml"):
                try:
                    with open(yaml_file, "r", encoding="utf-8") as f:
                        data = yaml.safe_load(f)
                        if data:
                            config.prompts.update(data)
                except Exception as e:
                    print(f"⚠️  Cảnh báo: Không thể load {yaml_file}: {e}")
        
        return config

    def validate(self) -> bool:
        """Kiểm tra cấu hình bắt buộc"""
        errors = []
        
        if not self.discord.token:
            errors.append("❌ Thiếu DISCORD_TOKEN trong file .env")
        
        if not self.gemini.api_key:
            errors.append("❌ Thiếu GEMINI_API_KEY trong file .env")
        
        if errors:
            print("\n=== LỖI CẤU HÌNH ===")
            for error in errors:
                print(error)
            print("===================\n")
            return False
        
        # In ra thông tin quota
        print(f"""
        ╔══════════════════════════════════════╗
        ║     📊 QUOTA SETTINGS              ║
        ║                                    ║
        ║  Max Tokens: {config.gemini.max_tokens:<6}               ║
        ║  History: {config.bot.max_history:<3} cặp tin nhắn       ║
        ║  Requests/phút: {config.gemini.max_requests_per_minute:<3}              ║
        ║                                    ║
        ║  💡 TIẾT KIỆM QUOTA TỐI ĐA       ║
        ╚══════════════════════════════════════╝
        """)
        
        return True

# Instance global
config = Config.load()