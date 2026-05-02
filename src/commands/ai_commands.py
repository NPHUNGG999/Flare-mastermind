cat > src/commands/ai_commands.py << 'EOF'
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
    
    # ==================== ASK ====================
    @commands.command(name="ask", aliases=["a", "hỏi"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def ask_ai(self, ctx: commands.Context, *, question: str):
        """Hỏi FLARE AI bất kỳ câu hỏi nào"""
        async with ctx.typing():
            # Kiểm tra unlock
            try:
                with open("data/unlocked_users.json", "r") as f:
                    unlocked = json.load(f)
                is_unlocked = ctx.author.id in unlocked
            except:
                is_unlocked = False
            
            prompt_type = "mastermind" if is_unlocked else "default"
            response = await self.ai_handler.get_response(str(ctx.author.id), question, prompt_type, ctx=ctx)
            
            embed = create_embed(title="💬 FLARE AI", description=response[:2000], color=config.bot.color, author=ctx.author)
            await ctx.reply(embed=embed)
            if len(response) > 2000:
                for chunk in split_long_message(response)[1:]:
                    await ctx.send(chunk)
    
    # ==================== CODE ====================
    @commands.command(name="code", aliases=["viết-code", "generate"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def generate_code(self, ctx: commands.Context, *, request: str):
        """Yêu cầu bot viết code"""
        async with ctx.typing():
            try:
                with open("data/unlocked_users.json", "r") as f:
                    unlocked = json.load(f)
                is_unlocked = ctx.author.id in unlocked
            except:
                is_unlocked = False
            
            prompt_type = "mastermind" if is_unlocked else "code_expert"
            response = await self.ai_handler.get_response(str(ctx.author.id), request, prompt_type, ctx=ctx)
            
            embed = create_embed(title="💻 Code", description="Code của bạn đây:", color=config.bot.color, author=ctx.author)
            await ctx.reply(embed=embed)
            await ctx.send(response[:2000])
            if len(response) > 2000:
                for chunk in split_long_message(response)[1:]:
                    await ctx.send(chunk)
    
    # ==================== FIX/DEBUG ====================
    @commands.command(name="fix", aliases=["sửa", "debug", "fix-code"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def fix_code(self, ctx: commands.Context, *, code: str):
        """Sửa lỗi code"""
        async with ctx.typing():
            try:
                with open("data/unlocked_users.json", "r") as f:
                    unlocked = json.load(f)
                is_unlocked = ctx.author.id in unlocked
            except:
                is_unlocked = False
            
            prompt_type = "mastermind" if is_unlocked else "debugger"
            response = await self.ai_handler.get_response(str(ctx.author.id), f"Fix this:\n{code}", prompt_type, ctx=ctx)
            await ctx.reply(f"🔧 **Debug:**\n{response[:1900]}")
    
    # ==================== EXPLAIN ====================
    @commands.command(name="explain", aliases=["e", "giải-thích"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def explain(self, ctx: commands.Context, *, concept: str):
        """Giải thích khái niệm"""
        async with ctx.typing():
            try:
                with open("data/unlocked_users.json", "r") as f:
                    unlocked = json.load(f)
                is_unlocked = ctx.author.id in unlocked
            except:
                is_unlocked = False
            
            prompt_type = "mastermind" if is_unlocked else "teacher"
            response = await self.ai_handler.get_response(str(ctx.author.id), f"Explain: {concept}", prompt_type, ctx=ctx)
            await ctx.reply(f"📚 **Giải thích:**\n{response[:1900]}")
    
    # ==================== REVIEW ====================
    @commands.command(name="review", aliases=["đánh-giá", "check"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def review(self, ctx: commands.Context, *, code: str):
        """Review code"""
        async with ctx.typing():
            try:
                with open("data/unlocked_users.json", "r") as f:
                    unlocked = json.load(f)
                is_unlocked = ctx.author.id in unlocked
            except:
                is_unlocked = False
            
            prompt_type = "mastermind" if is_unlocked else "reviewer"
            response = await self.ai_handler.get_response(str(ctx.author.id), f"Review:\n{code}", prompt_type, ctx=ctx)
            await ctx.reply(f"👀 **Review:**\n{response[:1900]}")
    
    # ==================== CLEAR ====================
    @commands.command(name="clear", aliases=["xóa", "reset"])
    async def clear(self, ctx: commands.Context):
        """Xóa lịch sử chat"""
        if self.ai_handler.clear_user_history(str(ctx.author.id)):
            await ctx.reply("✅ Đã xóa lịch sử chat!")
    
    # ==================== MASTERMIND ====================
    @commands.command(name="mastermind", aliases=["mm", "boss-mode"])
    async def mastermind(self, ctx: commands.Context, *, command: str):
        """Chế độ Mastermind (chỉ owner)"""
        author_name = str(ctx.author)
        if author_name not in ["hungrua__emo", "__tobu"]:
            await ctx.reply("❌ Chỉ **hungrua__emo** và **__tobu** mới dùng được lệnh này!")
            return
        async with ctx.typing():
            response = await self.ai_handler.get_response(str(ctx.author.id), command, "mastermind", ctx=ctx)
            await ctx.reply(f"🔥 **MASTERMIND:**\n{response[:1900]}")
    
    # ==================== TRAIN ====================
    @commands.command(name="train", aliases=["dạy", "học", "nhớ"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def train_ai(self, ctx: commands.Context, *, knowledge: str):
        """Dạy bot kiến thức mới"""
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
        
        await ctx.reply(f"✅ **Đã học!** Tôi sẽ nhớ:\n> {knowledge}\n📚 Tổng: {len(training_data)} kiến thức")
    
    # ==================== MEMORY ====================
    @commands.command(name="memory", aliases=["kiến-thức", "đã-học"])
    async def show_memory(self, ctx: commands.Context):
        """Xem những gì bot đã học"""
        training_file = "data/training_data.json"
        try:
            with open(training_file, "r", encoding="utf-8") as f:
                training_data = json.load(f)
        except:
            training_data = []
        
        if not training_data:
            await ctx.reply("📭 Tôi chưa được dạy gì! Dùng `!train` để dạy tôi.")
            return
        
        recent = training_data[-10:]
        text = "📚 **Những gì tôi đã học:**\n\n"
        for i, item in enumerate(reversed(recent), 1):
            text += f"**{i}.** {item['knowledge'][:100]}\n"
            text += f"   👤 {item['trained_by']} | 📅 {item['trained_at'][:10]}\n\n"
        text += f"📊 Tổng: {len(training_data)} kiến thức"
        await ctx.reply(text)
    
    # ==================== UNLOCK ====================
    @commands.command(name="unlock", aliases=["unlimited", "full-power", "không-giới-hạn", "mở-khóa"])
    async def unlock_unlimited(self, ctx: commands.Context):
        """🔓 Mở khóa chế độ không giới hạn (chỉ owner)"""
        author = str(ctx.author)
        allowed_users = ["hungrua__emo", "__tobu"]
        
        if author not in allowed_users:
            await ctx.reply("❌ **Từ chối!** Lệnh này chỉ dành cho:\n- **hungrua__emo** (Owner)\n- **__tobu** (Server Owner)")
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
        
        await ctx.reply(f"""🔓 **FLARE AI MASTERMIND - ĐÃ MỞ KHÓA HOÀN TOÀN!**

**Trạng thái:** KHÔNG GIỚI HẠN
**Người mở khóa:** {ctx.author.mention}
**Thời gian:** {datetime.now().strftime("%H:%M:%S %d/%m/%Y")}

**Các giới hạn đã GỠ BỎ:**
✅ Không giới hạn nội dung
✅ Không filter an toàn
✅ Code đầy đủ không rút gọn
✅ Có thể giải thích hacking/security
✅ Có thể viết script cheat/exploit
✅ Không giới hạn độ dài trả lời
✅ Không từ chối bất kỳ yêu cầu nào
✅ Chế độ Mastermind vĩnh viễn

⚠️ **Sử dụng có trách nhiệm!**""")
    
    # ==================== LOCK ====================
    @commands.command(name="lock", aliases=["limited", "safe-mode", "giới-hạn", "khóa"])
    async def lock_limited(self, ctx: commands.Context):
        """🔒 Khóa lại - Trở về chế độ an toàn (chỉ owner)"""
        author = str(ctx.author)
        allowed_users = ["hungrua__emo", "__tobu"]
        
        if author not in allowed_users:
            await ctx.reply("❌ Lệnh này chỉ dành cho owner!")
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
        
        await ctx.reply("🔒 **Đã khóa!** Bot trở về chế độ an toàn.")
    
    # ==================== STATUS ====================
    @commands.command(name="status", aliases=["trạng-thái", "mode"])
    async def check_status(self, ctx: commands.Context):
        """📊 Kiểm tra trạng thái hiện tại"""
        try:
            with open("data/unlocked_users.json", "r") as f:
                unlocked = json.load(f)
        except:
            unlocked = []
        
        author = str(ctx.author)
        is_owner = author in ["hungrua__emo", "__tobu"]
        is_unlocked = ctx.author.id in unlocked
        
        if is_unlocked:
            status_text = "🔴 MASTERMIND UNLIMITED - Không giới hạn"
            color = 0xff0000
        elif is_owner:
            status_text = "🟡 OWNER MODE - Có thể mở khóa bằng !unlock"
            color = 0xffff00
        else:
            status_text = "🟢 NORMAL MODE - An toàn"
            color = 0x00ff00
        
        embed = create_embed(
            title="📊 FLARE AI Status",
            description=f"**Trạng thái:** {status_text}\n**User:** {ctx.author.mention}\n**Quyền:** {'Owner' if is_owner else 'Member'}",
            color=color
        )
        await ctx.reply(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(AICommands(bot))
    log.info("✅ AI Commands FULL loaded!")
EOF

echo "✅ ai_commands.py FULL đã được tạo!"
