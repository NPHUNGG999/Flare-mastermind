import discord
from discord.ext import commands
from ..utils.config import config
from ..utils.helpers import split_long_message, create_embed
from ..utils.logger import get_logger
from ..ai.gemini_handler import GeminiHandler
import json
from datetime import datetime

log = get_logger(__name__)

class AICommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.ai_handler = GeminiHandler()
    
    @commands.command(name="ask", aliases=["a", "hoi"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def ask_ai(self, ctx: commands.Context, *, question: str):
        """Hoi FLARE AI bat ky cau hoi nao"""
        async with ctx.typing():
            try:
                with open("data/unlocked_users.json", "r") as f:
                    unlocked = json.load(f)
                is_unlocked = ctx.author.id in unlocked
            except:
                is_unlocked = False
            
            prompt_type = "mastermind" if is_unlocked else "default"
            response = await self.ai_handler.get_response(str(ctx.author.id), question, prompt_type, ctx=ctx)
            
            embed = create_embed(
                title="FLARE AI",
                description=response[:2000],
                color=config.bot.color,
                author=ctx.author
            )
            await ctx.reply(embed=embed)
            
            if len(response) > 2000:
                for chunk in split_long_message(response)[1:]:
                    await ctx.send(chunk)
    
    @commands.command(name="explain", aliases=["e", "giai-thich"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def explain(self, ctx: commands.Context, *, concept: str):
        """Giai thich khai niem"""
        async with ctx.typing():
            try:
                with open("data/unlocked_users.json", "r") as f:
                    unlocked = json.load(f)
                is_unlocked = ctx.author.id in unlocked
            except:
                is_unlocked = False
            
            prompt_type = "mastermind" if is_unlocked else "teacher"
            response = await self.ai_handler.get_response(str(ctx.author.id), f"Giai thich: {concept}", prompt_type, ctx=ctx)
            await ctx.reply(f"{response[:1900]}")
    
    @commands.command(name="clear", aliases=["xoa", "reset"])
    async def clear(self, ctx: commands.Context):
        """Xoa lich su chat voi AI"""
        if self.ai_handler.clear_user_history(str(ctx.author.id)):
            await ctx.reply("Da xoa lich su chat.")
        else:
            await ctx.reply("Khong co lich su de xoa.")
    
    @commands.command(name="train", aliases=["day", "hoc", "nho"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def train_ai(self, ctx: commands.Context, *, knowledge: str):
        """Day bot kien thuc moi"""
        training_file = "data/training_data.json"
        try:
            with open(training_file, "r", encoding="utf-8") as f:
                training_data = json.load(f)
        except:
            training_data = []
        
        training_data.append({
            "knowledge": knowledge,
            "trained_by": str(ctx.author),
            "trained_at": datetime.utcnow().isoformat(),
            "server": ctx.guild.name if ctx.guild else "DM"
        })
        
        with open(training_file, "w", encoding="utf-8") as f:
            json.dump(training_data, f, indent=2, ensure_ascii=False)
        
        await ctx.reply(f"Da hoc: {knowledge[:100]}\nTong: {len(training_data)} kien thuc")
    
    @commands.command(name="memory", aliases=["kien-thuc", "da-hoc"])
    async def show_memory(self, ctx: commands.Context):
        """Xem nhung gi bot da duoc day"""
        training_file = "data/training_data.json"
        try:
            with open(training_file, "r", encoding="utf-8") as f:
                training_data = json.load(f)
        except:
            training_data = []
        
        if not training_data:
            await ctx.reply("Chua duoc day kien thuc gi. Dung `!train` de day.")
            return
        
        recent = training_data[-10:]
        text = "**Kien thuc da hoc:**\n\n"
        for i, item in enumerate(reversed(recent), 1):
            text += f"**{i}.** {item['knowledge'][:100]}\n"
            text += f"    Day boi: {item['trained_by']}\n\n"
        text += f"**Tong:** {len(training_data)} kien thuc"
        
        await ctx.reply(text)
    
    @commands.command(name="unlock", aliases=["unlimited", "mo-khoa"])
    async def unlock_unlimited(self, ctx: commands.Context):
        """Mo khoa che do khong gioi han (chi owner)"""
        author = str(ctx.author)
        if author not in ["hungrua__emo", "__tobu"]:
            await ctx.reply("Chi hungrua__emo va __tobu moi duoc dung lenh nay.")
            return
        
        try:
            with open("data/unlocked_users.json", "r") as f:
                unlocked = json.load(f)
        except:
            unlocked = []
        
        if ctx.author.id not in unlocked:
            unlocked.append(ctx.author.id)
            with open("data/unlocked_users.json", "w") as f:
                json.dump(unlocked, f)
        
        await ctx.reply(f"Da mo khoa cho {ctx.author.mention}. Che do khong gioi han.")
    
    @commands.command(name="lock", aliases=["khoa"])
    async def lock_limited(self, ctx: commands.Context):
        """Khoa che do khong gioi han (chi owner)"""
        author = str(ctx.author)
        if author not in ["hungrua__emo", "__tobu"]:
            await ctx.reply("Chi hungrua__emo va __tobu moi duoc dung lenh nay.")
            return
        
        try:
            with open("data/unlocked_users.json", "r") as f:
                unlocked = json.load(f)
        except:
            unlocked = []
        
        if ctx.author.id in unlocked:
            unlocked.remove(ctx.author.id)
            with open("data/unlocked_users.json", "w") as f:
                json.dump(unlocked, f)
        
        await ctx.reply("Da khoa. Tro ve che do an toan.")
    
    @commands.command(name="status", aliases=["trang-thai", "mode"])
    async def check_status(self, ctx: commands.Context):
        """Kiem tra trang thai hien tai"""
        try:
            with open("data/unlocked_users.json", "r") as f:
                unlocked = json.load(f)
        except:
            unlocked = []
        
        author = str(ctx.author)
        is_owner = author in ["hungrua__emo", "__tobu"]
        is_unlocked = ctx.author.id in unlocked
        
        if is_unlocked:
            status_text = "UNLIMITED - Khong gioi han"
            color = 0xff0000
        elif is_owner:
            status_text = "OWNER - Co the mo khoa"
            color = 0xffff00
        else:
            status_text = "NORMAL - An toan"
            color = 0x00ffcc
        
        embed = create_embed(
            title="FLARE AI Status",
            description=f"**Trang thai:** {status_text}\n**Nguoi dung:** {ctx.author.mention}\n**Quyen:** {'Owner' if is_owner else 'Member'}",
            color=color
        )
        await ctx.reply(embed=embed)
    
    @commands.command(name="script", aliases=["s", "huong-dan"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def script_guide(self, ctx: commands.Context, *, question: str):
        """Huong dan su dung script"""
        async with ctx.typing():
            try:
                with open("data/unlocked_users.json", "r") as f:
                    unlocked = json.load(f)
                is_unlocked = ctx.author.id in unlocked
            except:
                is_unlocked = False
            
            prompt_type = "mastermind" if is_unlocked else "code_expert"
            response = await self.ai_handler.get_response(str(ctx.author.id), question, prompt_type, ctx=ctx)
            await ctx.reply(response[:2000])
    
    @commands.command(name="executor", aliases=["ex", "trinh-thuc-thi"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def executor_guide(self, ctx: commands.Context, *, executor_name: str):
        """Huong dan su dung executor"""
        async with ctx.typing():
            try:
                with open("data/unlocked_users.json", "r") as f:
                    unlocked = json.load(f)
                is_unlocked = ctx.author.id in unlocked
            except:
                is_unlocked = False
            
            prompt_type = "mastermind" if is_unlocked else "teacher"
            response = await self.ai_handler.get_response(
                str(ctx.author.id),
                f"Huong dan su dung executor {executor_name} de chay script Roblox",
                prompt_type,
                ctx=ctx
            )
            await ctx.reply(response[:2000])

async def setup(bot: commands.Bot):
    await bot.add_cog(AICommands(bot))
    log.info("AI Commands loaded!")
