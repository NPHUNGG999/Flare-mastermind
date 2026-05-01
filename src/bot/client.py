"""
============================================
 FLARE AI - Discord Bot Client
============================================
Bot client chính với đầy đủ tính năng
============================================
"""

import discord
from discord.ext import commands
from typing import Optional
from datetime import datetime
import asyncio

from ..utils.config import config
from ..utils.logger import get_logger

log = get_logger(__name__)

class FlareBot(commands.Bot):
    """
    FLARE AI Discord Bot Client
    
    Kế thừa từ commands.Bot với các tính năng:
    - Tự động load extensions
    - Custom presence
    - Error handling
    """
    
    def __init__(self):
        """Khởi tạo bot với intents đầy đủ"""
        
        # Thiết lập intents
        intents = discord.Intents.default()
        intents.message_content = True
        intents.messages = True
        intents.guilds = True
        intents.members = True
        intents.reactions = True
        
        # Khởi tạo bot
        super().__init__(
            command_prefix=config.discord.prefix,
            intents=intents,
            help_command=None,  # Sẽ dùng custom help
            case_insensitive=True,
            owner_id=config.discord.owner_id,
            description="FLARE AI - Trợ lý AI thông minh cho Discord"
        )
        
        # Lưu config
        self.config = config
        
        # Thời gian khởi động
        self.start_time: Optional[datetime] = None
        
        # Danh sách extensions cần load
        self.initial_extensions = [
            "src.commands.ai_commands",
            "src.commands.code_commands",
            "src.commands.utility_commands"
        ]
    
    async def setup_hook(self) -> None:
        """
        Hook được gọi trước khi bot chạy
        Dùng để load tất cả extensions/cogs
        """
        log.info("🔧 Đang thiết lập FLARE AI Bot...")
        
        # Load từng extension
        for extension in self.initial_extensions:
            try:
                await self.load_extension(extension)
                log.info(f"  ✅ Loaded: {extension}")
            except Exception as e:
                log.error(f"  ❌ Failed to load {extension}: {e}")
        
        log.info("✅ Tất cả extensions đã được load!")
    
    async def on_ready(self):
        """
        Sự kiện khi bot đã sẵn sàng
        """
        self.start_time = datetime.utcnow()
        
        # Log thông tin
        log.info(f"✅ {self.user.name} đã sẵn sàng hoạt động!")
        log.info(f"🆔 Bot ID: {self.user.id}")
        log.info(f"🌐 Đang phục vụ: {len(self.guilds)} servers")
        log.info(f"👥 Tổng users: {len(self.users)}")
        
        # Thiết lập status
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name=f"{config.discord.prefix}help | FLARE AI 🚀"
            ),
            status=discord.Status.online
        )
        
        # In banner đẹp ra console
        print(f"""
        ╔══════════════════════════════════════════╗
        ║          ✅ FLARE AI ONLINE!            ║
        ║                                          ║
        ║  🤖 Bot: {self.user.name:<30} ║
        ║  🆔 ID: {self.user.id:<31} ║
        ║  📝 Prefix: {config.discord.prefix:<27} ║
        ║  🌐 Servers: {len(self.guilds):<26} ║
        ║  👥 Users: {len(self.users):<28} ║
        ║                                          ║
        ║  🟢 Status: ONLINE                       ║
        ╚══════════════════════════════════════════╝
        """)
    
    async def on_error(self, event_method: str, *args, **kwargs):
        """Xử lý lỗi toàn cục"""
        log.exception(f"Lỗi trong sự kiện {event_method}")
    
    def run_bot(self):
        """Chạy bot với token từ config"""
        if not config.validate():
            raise ValueError("Cấu hình không hợp lệ! Kiểm tra file .env")
        
        log.info(f"🚀 Đang khởi động {config.bot.name}...")
        super().run(config.discord.token, log_handler=None)
