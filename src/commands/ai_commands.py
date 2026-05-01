"""
============================================
 FLARE AI - AI Commands
============================================
Commands liên quan đến chat AI (Gemini)
============================================
"""

import discord
from discord.ext import commands
from typing import Optional

from ..utils.config import config
from ..utils.helpers import split_long_message, create_embed
from ..utils.logger import get_logger
from ..ai.gemini_handler import GeminiHandler  # ĐỔI IMPORT

log = get_logger(__name__)

class AICommands(commands.Cog):
    """
    Commands AI cơ bản
    
    Commands:
    - ask: Hỏi AI
    - explain: Giải thích
    - chat: Chat với AI
    """
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.ai_handler = GeminiHandler()  # ĐỔI THÀNH GeminiHandler
    
    @commands.command(name="ask", aliases=["a", "hỏi"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def ask_ai(self, ctx: commands.Context, *, question: str):
        """
        Hỏi FLARE AI bất kỳ câu hỏi nào
        
        Cách dùng: !ask <câu hỏi của bạn>
        Ví dụ: !ask Python có những framework web nào?
        """
        async with ctx.typing():
            # Lấy câu trả lời từ Gemini
            response = await self.ai_handler.get_response(
                user_id=str(ctx.author.id),
                message=question,
                prompt_type="default"
            )
            
            # Tạo embed đẹp
            embed = create_embed(
                title="💬 FLARE AI Trả Lời",
                description=response[:2000] if len(response) <= 2000 else response[:1997] + "...",
                color=config.bot.color,
                author=ctx.author,
                footer=f"Powered by Google Gemini | !clear để xóa lịch sử"
            )
            
            await ctx.reply(embed=embed)
            
            # Nếu response quá dài, gửi tiếp các phần còn lại
            if len(response) > 2000:
                chunks = split_long_message(response)
                for i, chunk in enumerate(chunks):
                    if i > 0:
                        await ctx.send(f"**...tiếp theo:**\n{chunk}")
    
    @commands.command(name="explain", aliases=["e", "giải-thích"])
    @commands.cooldown(1, 8, commands.BucketType.user)
    async def explain_concept(self, ctx: commands.Context, *, concept: str):
        """
        Yêu cầu FLARE AI giải thích một khái niệm
        
        Cách dùng: !explain <khái niệm>
        Ví dụ: !explain event loop trong JavaScript
        """
        async with ctx.typing():
            response = await self.ai_handler.get_response(
                user_id=str(ctx.author.id),
                message=f"Please explain this concept in detail: {concept}",
                prompt_type="teacher"
            )
            
            embed = create_embed(
                title="📚 Giải Thích",
                description=response[:2000] if len(response) <= 2000 else response[:1997] + "...",
                color=config.bot.color,
                author=ctx.author,
                footer="FLARE AI Teacher Mode | Gemini Powered"
            )
            
            await ctx.reply(embed=embed)
            
            if len(response) > 2000:
                chunks = split_long_message(response)
                for chunk in chunks[1:]:
                    await ctx.send(chunk)
    
    @commands.command(name="chat", aliases=["c", "nói-chuyện"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def chat_with_ai(self, ctx: commands.Context, *, message: str):
        """
        Chat tự nhiên với FLARE AI
        
        Cách dùng: !chat <tin nhắn>
        Ví dụ: !chat Bạn có khỏe không?
        """
        async with ctx.typing():
            response = await self.ai_handler.get_response(
                user_id=str(ctx.author.id),
                message=message,
                prompt_type="default"
            )
            
            await ctx.reply(response)
    
    @commands.command(name="clear", aliases=["xóa", "reset"])
    async def clear_history(self, ctx: commands.Context):
        """
        Xóa lịch sử chat với AI
        
        Cách dùng: !clear
        """
        if self.ai_handler.clear_user_history(str(ctx.author.id)):
            await ctx.reply("✅ Đã xóa lịch sử trò chuyện của bạn!")
        else:
            await ctx.reply("❌ Không thể xóa lịch sử. Vui lòng thử lại!")

async def setup(bot: commands.Bot):
    """Setup function để load cog"""
    await bot.add_cog(AICommands(bot))
    log.info("✅ AI Commands loaded!")