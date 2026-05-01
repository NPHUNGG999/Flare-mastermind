"""
============================================
 FLARE AI - Event Handlers
============================================
Xử lý tất cả sự kiện Discord
============================================
"""

import discord
from discord.ext import commands
from typing import Optional
import asyncio

from ..utils.logger import get_logger
from ..utils.config import config
from ..utils.helpers import split_long_message, create_embed
from ..ai.gemini_handler import GeminiHandler  # ĐỔI TỪ OpenAIHandler
from ..ai.conversation import ConversationManager

log = get_logger(__name__)

# Khởi tạo handlers
ai_handler = GeminiHandler()  # ĐỔI THÀNH GeminiHandler
conversation_manager = ConversationManager()

def setup_events(bot: commands.Bot):
    """
    Đăng ký tất cả event handlers cho bot
    
    Args:
        bot: Discord Bot instance
    """
    
    @bot.event
    async def on_message(message: discord.Message):
        """
        Xử lý tin nhắn đến
        
        Flow:
        1. Bỏ qua tin nhắn từ bot
        2. Xử lý commands
        3. Xử lý DM
        4. Xử lý mentions
        """
        # 1. Bỏ qua tin nhắn của chính bot
        if message.author == bot.user:
            return
        
        # 2. Xử lý commands (luôn luôn)
        await bot.process_commands(message)
        
        # 3. Xử lý Direct Messages
        if isinstance(message.channel, discord.DMChannel):
            await handle_dm_message(bot, message)
            return
        
        # 4. Xử lý mentions trong server
        if bot.user in message.mentions:
            await handle_mention_message(bot, message)
    
    @bot.event
    async def on_guild_join(guild: discord.Guild):
        """Bot tham gia server mới"""
        log.info(f"🌟 Tham gia server mới: {guild.name} (ID: {guild.id})")
        
        # Tìm channel để gửi welcome message
        target_channel = (
            guild.system_channel or
            next((c for c in guild.text_channels 
                  if c.permissions_for(guild.me).send_messages), None)
        )
        
        if target_channel:
            embed = create_embed(
                title="🌟 FLARE AI Đã Tham Gia Server!",
                description=(
                    f"Cảm ơn bạn đã mời **{bot.user.name}**!\n\n"
                    f"📝 **Prefix:** `{config.discord.prefix}`\n"
                    f"💡 **Bắt đầu:** Gõ `{config.discord.prefix}help`\n"
                    f"💬 **Chat:** Tag bot để trò chuyện\n\n"
                    f"🚀 **Powered by Google Gemini**\n"
                    f"Chúc bạn có trải nghiệm tuyệt vời!"
                ),
                color=config.bot.color,
                thumbnail=bot.user.display_avatar.url if bot.user.display_avatar else None,
                footer=f"FLARE AI v1.0.0 | Gemini Powered"
            )
            
            try:
                await target_channel.send(embed=embed)
            except Exception as e:
                log.error(f"Không thể gửi welcome message: {e}")
    
    @bot.event
    async def on_guild_remove(guild: discord.Guild):
        """Bot rời server"""
        log.info(f"👋 Rời server: {guild.name} (ID: {guild.id})")
    
    @bot.event
    async def on_command_error(ctx: commands.Context, error: Exception):
        """Xử lý lỗi commands"""
        if isinstance(error, commands.CommandNotFound):
            await ctx.send(
                f"❌ Không tìm thấy lệnh! Gõ `{config.discord.prefix}help` để xem danh sách.",
                delete_after=10
            )
        elif isinstance(error, commands.MissingPermissions):
            missing = ", ".join(error.missing_permissions)
            await ctx.send(
                f"❌ Bạn cần quyền `{missing}` để dùng lệnh này!",
                delete_after=10
            )
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(
                f"⏰ Chậm lại nào! Vui lòng đợi {error.retry_after:.1f}s.",
                delete_after=10
            )
        else:
            log.error(f"Command error: {error}", exc_info=True)
            await ctx.send(
                f"❌ Có lỗi xảy ra: {str(error)[:100]}",
                delete_after=15
            )

async def handle_dm_message(bot: commands.Bot, message: discord.Message):
    """Xử lý tin nhắn riêng (DM)"""
    async with message.channel.typing():
        try:
            response = await ai_handler.get_response(
                user_id=str(message.author.id),
                message=message.content,
                prompt_type="default"
            )
            
            if len(response) > 2000:
                chunks = split_long_message(response)
                for chunk in chunks:
                    await message.reply(chunk)
            else:
                await message.reply(response)
                
        except Exception as e:
            log.error(f"Lỗi xử lý DM: {e}")
            await message.reply("❌ Có lỗi xảy ra khi xử lý tin nhắn của bạn.")

async def handle_mention_message(bot: commands.Bot, message: discord.Message):
    """Xử lý khi bot được mention"""
    content = message.content.replace(f'<@{bot.user.id}>', '').strip()
    
    if not content:
        await message.reply(
            f"👋 Xin chào! Tôi là **{bot.user.name}**!\n"
            f"🚀 Powered by **Google Gemini**\n"
            f"Gõ `{config.discord.prefix}help` để xem các lệnh hỗ trợ."
        )
        return
    
    async with message.channel.typing():
        try:
            response = await ai_handler.get_response(
                user_id=str(message.author.id),
                message=content,
                prompt_type="default"
            )
            
            if len(response) > 2000:
                chunks = split_long_message(response)
                for i, chunk in enumerate(chunks):
                    if i == 0:
                        await message.reply(chunk)
                    else:
                        await message.channel.send(chunk)
            else:
                await message.reply(response)
                
        except Exception as e:
            log.error(f"Lỗi xử lý mention: {e}")
            await message.reply("❌ Có lỗi xảy ra. Vui lòng thử lại sau!")