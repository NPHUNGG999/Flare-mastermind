"""
============================================
 FLARE AI - Code Commands
============================================
Commands hỗ trợ lập trình (Gemini)
============================================
"""

import discord
from discord.ext import commands
from typing import Optional

from ..utils.config import config
from ..utils.helpers import split_long_message, create_embed, format_code_block
from ..utils.logger import get_logger
from ..ai.gemini_handler import GeminiHandler  # ĐỔI IMPORT

log = get_logger(__name__)

class CodeCommands(commands.Cog):
    """
    Commands hỗ trợ code
    
    Commands:
    - code: Viết code
    - fix: Sửa lỗi
    - review: Review code
    - optimize: Tối ưu code
    - convert: Chuyển đổi ngôn ngữ
    """
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.ai_handler = GeminiHandler()  # ĐỔI THÀNH GeminiHandler
    
    @commands.command(name="code", aliases=["viết-code", "generate"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def generate_code(self, ctx: commands.Context, *, request: str):
        """
        Yêu cầu FLARE AI viết code
        
        Cách dùng: !code <yêu cầu>
        Ví dụ: !code hàm sắp xếp mảng trong Python
        """
        async with ctx.typing():
            response = await self.ai_handler.get_response(
                user_id=str(ctx.author.id),
                message=f"Write code for the following request. Include comments and explanation:\n{request}",
                prompt_type="code_expert"
            )
            
            embed = create_embed(
                title="💻 Code Generated",
                description="Dưới đây là code theo yêu cầu của bạn:",
                color=config.bot.color,
                author=ctx.author,
                footer="FLARE AI Code Expert | Gemini Powered"
            )
            
            await ctx.reply(embed=embed)
            
            if len(response) > 2000:
                chunks = split_long_message(response)
                for chunk in chunks:
                    await ctx.send(chunk)
            else:
                await ctx.send(response)
    
    @commands.command(name="fix", aliases=["sửa", "debug", "sửa-lỗi"])
    @commands.cooldown(1, 8, commands.BucketType.user)
    async def fix_code(self, ctx: commands.Context, *, code: str):
        """
        Sửa lỗi code hoặc debug
        
        Cách dùng: !fix <code bị lỗi hoặc error message>
        Ví dụ: !fix print("Hello)
        """
        async with ctx.typing():
            response = await self.ai_handler.get_response(
                user_id=str(ctx.author.id),
                message=f"Fix this code or debug this error:\n{code}",
                prompt_type="debugger"
            )
            
            embed = create_embed(
                title="🔧 Debug Result",
                description="Kết quả sửa lỗi:",
                color=0xff6b6b,
                author=ctx.author,
                footer="FLARE AI Debug Expert | Gemini Powered"
            )
            
            await ctx.reply(embed=embed)
            
            if len(response) > 2000:
                chunks = split_long_message(response)
                for chunk in chunks:
                    await ctx.send(chunk)
            else:
                await ctx.send(response)
    
    @commands.command(name="review", aliases=["đánh-giá", "check"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def review_code(self, ctx: commands.Context, *, code: str):
        """
        Yêu cầu FLARE AI review code
        
        Cách dùng: !review <code cần review>
        Ví dụ: !review def hello(): print("world")
        """
        async with ctx.typing():
            response = await self.ai_handler.get_response(
                user_id=str(ctx.author.id),
                message=f"Review this code and suggest improvements:\n{code}",
                prompt_type="reviewer"
            )
            
            embed = create_embed(
                title="👀 Code Review",
                description="Đánh giá code của bạn:",
                color=0xffd93d,
                author=ctx.author,
                footer="FLARE AI Code Reviewer | Gemini Powered"
            )
            
            await ctx.reply(embed=embed)
            
            if len(response) > 2000:
                chunks = split_long_message(response)
                for chunk in chunks:
                    await ctx.send(chunk)
            else:
                await ctx.send(response)
    
    @commands.command(name="optimize", aliases=["tối-ưu", "improve"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def optimize_code(self, ctx: commands.Context, *, code: str):
        """
        Tối ưu hóa code
        
        Cách dùng: !optimize <code cần tối ưu>
        """
        async with ctx.typing():
            response = await self.ai_handler.get_response(
                user_id=str(ctx.author.id),
                message=f"Optimize this code for better performance and readability:\n{code}",
                prompt_type="code_expert"
            )
            
            embed = create_embed(
                title="⚡ Optimized Code",
                color=0x4ecdc4,
                author=ctx.author,
                footer="Gemini Powered"
            )
            
            await ctx.reply(embed=embed)
            
            if len(response) > 2000:
                chunks = split_long_message(response)
                for chunk in chunks:
                    await ctx.send(chunk)
            else:
                await ctx.send(response)
    
    @commands.command(name="convert", aliases=["chuyển-đổi"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def convert_code(
        self,
        ctx: commands.Context,
        target_language: str,
        *,
        code: str
    ):
        """
        Chuyển đổi code sang ngôn ngữ khác
        
        Cách dùng: !convert <ngôn ngữ đích> <code>
        Ví dụ: !convert python console.log("hello")
        """
        async with ctx.typing():
            response = await self.ai_handler.get_response(
                user_id=str(ctx.author.id),
                message=f"Convert this code to {target_language}:\n{code}",
                prompt_type="code_expert"
            )
            
            await ctx.reply(
                f"🔄 **Chuyển đổi sang {target_language}:**\n{response[:1900]}"
            )

async def setup(bot: commands.Bot):
    """Setup function để load cog"""
    await bot.add_cog(CodeCommands(bot))
    log.info("✅ Code Commands loaded!")