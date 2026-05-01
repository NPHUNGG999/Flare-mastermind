"""
============================================
 FLARE AI - Utility Commands
============================================
Commands tiện ích đầy đủ cho bot
============================================
"""

import discord
from discord.ext import commands
import platform
import time
import psutil
import os
from datetime import datetime, timedelta

from ..utils.config import config
from ..utils.helpers import split_long_message, create_embed
from ..utils.logger import get_logger
from ..ai.gemini_handler import GeminiHandler

log = get_logger(__name__)

class UtilityCommands(commands.Cog):
    """
    Commands tiện ích đầy đủ
    
    Commands:
    - help: Hiển thị trợ giúp chi tiết
    - ping: Kiểm tra ping bot
    - info: Thông tin chi tiết về bot
    - stats: Thống kê sử dụng
    - invite: Link mời bot
    - uptime: Thời gian bot đã chạy
    - serverinfo: Thông tin server
    - userinfo: Thông tin user
    - avatar: Xem avatar
    - suggest: Gửi góp ý
    """
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.start_time = datetime.utcnow()
        self.ai_handler = GeminiHandler()
    
    # ==================== HELP ====================
    
    @commands.command(name="help", aliases=["h", "trợ-giúp", "lệnh", "cmds"])
    async def help_command(self, ctx: commands.Context, *, query: str = None):
        """
        Hiển thị danh sách lệnh và hướng dẫn chi tiết
        
        Cách dùng:
        • !help - Xem tất cả lệnh
        • !help <tên lệnh> - Xem chi tiết 1 lệnh
        • !help ai - Xem nhóm lệnh AI
        • !help code - Xem nhóm lệnh Code
        
        Ví dụ:
        • !help ask
        • !help code
        """
        
        # Nếu query là tên lệnh cụ thể
        if query:
            # Kiểm tra xem có phải tên lệnh không
            command = self.bot.get_command(query.lower())
            if command:
                return await self._show_command_help(ctx, command)
            
            # Kiểm tra xem có phải nhóm lệnh không
            if query.lower() in ['ai', 'chat', 'hỏi']:
                return await self._show_category_help(ctx, "AI", [
                    ("ask", "Hỏi AI bất kỳ câu hỏi nào"),
                    ("chat", "Chat tự nhiên với AI"),
                    ("explain", "Giải thích khái niệm"),
                    ("clear", "Xóa lịch sử chat")
                ])
            elif query.lower() in ['code', 'lập-trình', 'dev']:
                return await self._show_category_help(ctx, "Code", [
                    ("code", "Viết code theo yêu cầu"),
                    ("fix", "Sửa lỗi code / debug"),
                    ("review", "Review code"),
                    ("optimize", "Tối ưu hóa code"),
                    ("convert", "Chuyển đổi ngôn ngữ")
                ])
            elif query.lower() in ['utility', 'tiện-ích', 'tool']:
                return await self._show_category_help(ctx, "Tiện ích", [
                    ("ping", "Kiểm tra ping"),
                    ("info", "Thông tin bot"),
                    ("stats", "Thống kê"),
                    ("uptime", "Thời gian hoạt động"),
                    ("serverinfo", "Thông tin server"),
                    ("userinfo", "Thông tin user"),
                    ("avatar", "Xem avatar"),
                    ("invite", "Link mời bot"),
                    ("suggest", "Gửi góp ý")
                ])
            
            # Không tìm thấy
            await ctx.send(f"❌ Không tìm thấy lệnh hoặc nhóm: `{query}`")
            return
        
        # ===== HELP TỔNG QUÁT =====
        
        # Tạo embed chính
        embed = discord.Embed(
            title="🌟 FLARE AI - Trung Tâm Trợ Giúp",
            description=(
                f"**Chào mừng đến với FLARE AI!**\n"
                f"Bot AI thông minh hỗ trợ lập trình và trò chuyện\n\n"
                f"📝 **Prefix:** `{config.discord.prefix}`\n"
                f"💬 **Chat nhanh:** Tag @{self.bot.user.name} <tin nhắn>\n"
                f"🔍 **Chi tiết:** `{config.discord.prefix}help <lệnh>`\n\n"
                f"**Chọn danh mục bên dưới để xem chi tiết:**"
            ),
            color=config.bot.color,
            timestamp=datetime.utcnow()
        )
        
        # Thông tin bot
        embed.add_field(
            name="🤖 Thông Tin Bot",
            value=(
                f"**Tên:** {config.bot.name}\n"
                f"**Phiên bản:** v1.0.0\n"
                f"**Engine:** Google Gemini\n"
                f"**Model:** {config.gemini.model}\n"
                f"**Ping:** {round(self.bot.latency * 1000)}ms\n"
                f"**Servers:** {len(self.bot.guilds)}\n"
                f"**Users:** {len(self.bot.users)}"
            ),
            inline=False
        )
        
        # Danh mục lệnh
        embed.add_field(
            name="💬 Lệnh AI Chat",
            value=(
                f"`{config.discord.prefix}ask` - Hỏi AI\n"
                f"`{config.discord.prefix}chat` - Chat với AI\n"
                f"`{config.discord.prefix}explain` - Giải thích\n"
                f"`{config.discord.prefix}clear` - Xóa lịch sử\n"
                f"➡️ `{config.discord.prefix}help ai` để xem chi tiết"
            ),
            inline=True
        )
        
        embed.add_field(
            name="💻 Lệnh Code",
            value=(
                f"`{config.discord.prefix}code` - Viết code\n"
                f"`{config.discord.prefix}fix` - Sửa lỗi\n"
                f"`{config.discord.prefix}review` - Review\n"
                f"`{config.discord.prefix}optimize` - Tối ưu\n"
                f"`{config.discord.prefix}convert` - Chuyển đổi\n"
                f"➡️ `{config.discord.prefix}help code`"
            ),
            inline=True
        )
        
        embed.add_field(
            name="🔧 Lệnh Tiện Ích",
            value=(
                f"`{config.discord.prefix}ping` - Kiểm tra ping\n"
                f"`{config.discord.prefix}info` - Thông tin bot\n"
                f"`{config.discord.prefix}stats` - Thống kê\n"
                f"`{config.discord.prefix}uptime` - Uptime\n"
                f"`{config.discord.prefix}serverinfo` - Server\n"
                f"`{config.discord.prefix}userinfo` - User\n"
                f"`{config.discord.prefix}avatar` - Avatar\n"
                f"`{config.discord.prefix}invite` - Mời bot\n"
                f"➡️ `{config.discord.prefix}help utility`"
            ),
            inline=True
        )
        
        # Mẹo sử dụng
        embed.add_field(
            name="💡 Mẹo Sử Dụng",
            value=(
                f"• Tag bot để chat nhanh: @{self.bot.user.name} hello\n"
                f"• Gửi code trong ``` ``` để AI hiểu rõ hơn\n"
                f"• Dùng `{config.discord.prefix}clear` để reset chat\n"
                f"• AI nhớ 3 tin nhắn gần nhất để trả lời mạch lạc\n"
                f"• Bot miễn phí 100% nhờ Google Gemini API"
            ),
            inline=False
        )
        
        # Footer
        embed.set_footer(
            text=f"FLARE AI v1.0.0 • {len(self.bot.commands)} lệnh • Gemini Powered",
            icon_url=self.bot.user.display_avatar.url if self.bot.user.display_avatar else None
        )
        
        # Thêm thumbnail
        if self.bot.user.display_avatar:
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        
        await ctx.send(embed=embed)
    
    async def _show_command_help(self, ctx, command):
        """Hiển thị help cho 1 lệnh cụ thể"""
        embed = discord.Embed(
            title=f"📖 Lệnh: {config.discord.prefix}{command.qualified_name}",
            description=command.help or "Không có mô tả chi tiết",
            color=config.bot.color,
            timestamp=datetime.utcnow()
        )
        
        # Cách sử dụng
        usage = f"`{config.discord.prefix}{command.qualified_name}"
        if command.signature:
            usage += f" {command.signature}"
        usage += "`"
        embed.add_field(name="📝 Cách Dùng", value=usage, inline=False)
        
        # Aliases
        if command.aliases:
            aliases = ", ".join([f"`{config.discord.prefix}{a}`" for a in command.aliases])
            embed.add_field(name="🔄 Aliases", value=aliases, inline=False)
        
        # Cooldown
        if command._buckets:
            cooldown = command._buckets._cooldown
            if cooldown:
                embed.add_field(
                    name="⏰ Cooldown",
                    value=f"{cooldown.rate} lần / {cooldown.per:.0f}s",
                    inline=True
                )
        
        # Category
        cog = command.cog_name or "Không có"
        embed.add_field(name="📂 Nhóm", value=cog, inline=True)
        
        embed.set_footer(text=f"FLARE AI Help System")
        await ctx.send(embed=embed)
    
    async def _show_category_help(self, ctx, category_name, commands_list):
        """Hiển thị help cho 1 nhóm lệnh"""
        embed = discord.Embed(
            title=f"📂 Nhóm Lệnh: {category_name}",
            description=f"Danh sách lệnh trong nhóm **{category_name}**:",
            color=config.bot.color,
            timestamp=datetime.utcnow()
        )
        
        for cmd_name, cmd_desc in commands_list:
            command = self.bot.get_command(cmd_name)
            if command:
                embed.add_field(
                    name=f"{config.discord.prefix}{cmd_name}",
                    value=f"{cmd_desc}\nDùng `{config.discord.prefix}help {cmd_name}` để xem chi tiết",
                    inline=False
                )
        
        embed.set_footer(text=f"FLARE AI • Nhóm {category_name}")
        await ctx.send(embed=embed)
    
    # ==================== PING ====================
    
    @commands.command(name="ping", aliases=["p", "latency"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def ping(self, ctx: commands.Context):
        """
        Kiểm tra độ trễ và tốc độ phản hồi của bot
        
        Cách dùng: !ping
        
        Hiển thị:
        • WebSocket latency
        • Message response time
        • API response time
        """
        # Đo thời gian
        start = time.monotonic()
        
        # Gửi tin nhắn test
        msg = await ctx.send("🏓 **Đang đo ping...**")
        
        # Tính latency
        message_latency = round((time.monotonic() - start) * 1000)
        ws_latency = round(self.bot.latency * 1000)
        
        # Đánh giá chất lượng
        if ws_latency < 100:
            quality = "🟢 Xuất sắc"
            color = 0x00ff00
        elif ws_latency < 200:
            quality = "🟡 Ổn định"
            color = 0xffff00
        else:
            quality = "🔴 Chậm"
            color = 0xff0000
        
        # Tạo embed
        embed = discord.Embed(
            title="🏓 Pong! Kết Quả Ping",
            color=color,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="📡 WebSocket",
            value=f"```{ws_latency}ms```",
            inline=True
        )
        embed.add_field(
            name="💬 Message",
            value=f"```{message_latency}ms```",
            inline=True
        )
        embed.add_field(
            name="📊 Chất Lượng",
            value=f"```{quality}```",
            inline=True
        )
        
        # Thông tin thêm
        embed.add_field(
            name="🖥️ Server",
            value=f"```{len(self.bot.guilds)} servers```",
            inline=True
        )
        embed.add_field(
            name="👥 Users",
            value=f"```{len(self.bot.users)} users```",
            inline=True
        )
        embed.add_field(
            name="⏰ Uptime",
            value=f"```{self._get_uptime()}```",
            inline=True
        )
        
        embed.set_footer(text="FLARE AI Network Diagnostics")
        
        await msg.edit(content=None, embed=embed)
    
    # ==================== INFO ====================
    
    @commands.command(name="info", aliases=["i", "thông-tin", "about", "botinfo"])
    async def info(self, ctx: commands.Context):
        """
        Hiển thị thông tin chi tiết về FLARE AI Bot
        
        Cách dùng: !info
        
        Bao gồm:
        • Phiên bản, tác giả
        • Công nghệ sử dụng
        • Thống kê hoạt động
        • Tài nguyên hệ thống
        """
        
        # Lấy thông tin hệ thống
        process = psutil.Process(os.getpid())
        memory_usage = process.memory_info().rss / 1024 / 1024  # MB
        cpu_usage = process.cpu_percent(interval=1)
        
        # Tạo embed
        embed = discord.Embed(
            title=f"🤖 {config.bot.name} - Thông Tin Chi Tiết",
            description="AI-powered Discord Bot sử dụng Google Gemini",
            color=config.bot.color,
            timestamp=datetime.utcnow()
        )
        
        # Avatar
        if self.bot.user.display_avatar:
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        
        # Thông tin cơ bản
        embed.add_field(
            name="📌 Thông Tin Cơ Bản",
            value=(
                f"**Tên:** {self.bot.user.name}\n"
                f"**ID:** `{self.bot.user.id}`\n"
                f"**Phiên bản:** v1.0.0\n"
                f"**Prefix:** `{config.discord.prefix}`\n"
                f"**Ngày tạo:** {self.bot.user.created_at.strftime('%d/%m/%Y')}"
            ),
            inline=False
        )
        
        # Công nghệ
        embed.add_field(
            name="⚙️ Công Nghệ",
            value=(
                f"**Python:** {platform.python_version()}\n"
                f"**Discord.py:** {discord.__version__}\n"
                f"**AI Engine:** Google Gemini\n"
                f"**Model:** {config.gemini.model}\n"
                f"**Max Tokens:** {config.gemini.max_tokens}"
            ),
            inline=True
        )
        
        # Thống kê
        uptime = self._get_uptime()
        embed.add_field(
            name="📊 Thống Kê",
            value=(
                f"**Servers:** {len(self.bot.guilds)}\n"
                f"**Users:** {len(self.bot.users)}\n"
                f"**Commands:** {len(self.bot.commands)}\n"
                f"**Uptime:** {uptime}\n"
                f"**Ping:** {round(self.bot.latency * 1000)}ms"
            ),
            inline=True
        )
        
        # Hệ thống
        embed.add_field(
            name="🖥️ Hệ Thống",
            value=(
                f"**RAM:** {memory_usage:.1f} MB\n"
                f"**CPU:** {cpu_usage}%\n"
                f"**OS:** {platform.system()}\n"
                f"**Python:** {platform.python_version()}"
            ),
            inline=True
        )
        
        # Links
        embed.add_field(
            name="🔗 Liên Kết",
            value=(
                f"**Mời Bot:** [Click Here](https://discord.com/oauth2/authorize?client_id={self.bot.user.id}&permissions=2147485696&scope=bot)\n"
                f"**GitHub:** [FLARE AI](https://github.com)\n"
                f"**Hỗ Trợ:** Dùng `{config.discord.prefix}suggest`"
            ),
            inline=False
        )
        
        embed.set_footer(
            text=f"FLARE AI • Made with ❤️",
            icon_url=self.bot.user.display_avatar.url if self.bot.user.display_avatar else None
        )
        
        await ctx.send(embed=embed)
    
    # ==================== STATS ====================
    
    @commands.command(name="stats", aliases=["thống-kê", "statistics"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def stats(self, ctx: commands.Context):
        """
        Hiển thị thống kê sử dụng FLARE AI
        
        Cách dùng: !stats
        """
        ai_stats = self.ai_handler.get_stats()
        
        embed = discord.Embed(
            title="📊 FLARE AI - Thống Kê Sử Dụng",
            color=config.bot.color,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="🧠 AI Stats",
            value=(
                f"**Model:** {ai_stats.get('model', 'N/A')}\n"
                f"**Max Tokens:** {ai_stats.get('max_tokens', 'N/A')}\n"
                f"**Requests/min:** {ai_stats.get('requests_this_minute', 'N/A')}\n"
                f"**Conversations:** {ai_stats.get('total_conversations', 0)}\n"
                f"**Total Messages:** {ai_stats.get('total_messages', 0)}"
            ),
            inline=False
        )
        
        embed.add_field(
            name="🌐 Discord Stats",
            value=(
                f"**Servers:** {len(self.bot.guilds)}\n"
                f"**Users:** {len(self.bot.users)}\n"
                f"**Commands:** {len(self.bot.commands)}\n"
                f"**Uptime:** {self._get_uptime()}\n"
                f"**Ping:** {round(self.bot.latency * 1000)}ms"
            ),
            inline=False
        )
        
        embed.set_footer(text="FLARE AI Analytics")
        await ctx.send(embed=embed)
    
    # ==================== UPTIME ====================
    
    @commands.command(name="uptime", aliases=["up", "thời-gian"])
    async def uptime(self, ctx: commands.Context):
        """
        Xem thời gian bot đã hoạt động
        
        Cách dùng: !uptime
        """
        uptime_str = self._get_uptime()
        started = self.start_time.strftime("%d/%m/%Y %H:%M:%S UTC")
        
        embed = discord.Embed(
            title="⏰ FLARE AI Uptime",
            color=config.bot.color,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="🟢 Đã Hoạt Động",
            value=f"```{uptime_str}```",
            inline=False
        )
        embed.add_field(
            name="📅 Bắt Đầu Từ",
            value=f"```{started}```",
            inline=False
        )
        
        embed.set_footer(text="FLARE AI • 24/7 Online")
        await ctx.send(embed=embed)
    
    # ==================== SERVER INFO ====================
    
    @commands.command(name="serverinfo", aliases=["si", "guild", "server"])
    async def server_info(self, ctx: commands.Context):
        """
        Hiển thị thông tin chi tiết về server
        
        Cách dùng: !serverinfo
        """
        guild = ctx.guild
        
        if not guild:
            await ctx.send("❌ Lệnh này chỉ dùng trong server!")
            return
        
        # Đếm members
        total_members = guild.member_count
        online_members = sum(1 for m in guild.members if m.status != discord.Status.offline)
        bots = sum(1 for m in guild.members if m.bot)
        humans = total_members - bots
        
        # Đếm channels
        text_channels = len(guild.text_channels)
        voice_channels = len(guild.voice_channels)
        
        # Đếm roles
        roles = len(guild.roles)
        
        # Boost
        boost_level = guild.premium_tier
        boost_count = guild.premium_subscription_count
        
        # Ngày tạo
        created_at = guild.created_at.strftime("%d/%m/%Y")
        
        embed = discord.Embed(
            title=f"📊 {guild.name} - Server Info",
            color=config.bot.color,
            timestamp=datetime.utcnow()
        )
        
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        
        embed.add_field(
            name="📌 Thông Tin Cơ Bản",
            value=(
                f"**Tên:** {guild.name}\n"
                f"**ID:** `{guild.id}`\n"
                f"**Owner:** {guild.owner.mention if guild.owner else 'N/A'}\n"
                f"**Ngày tạo:** {created_at}\n"
                f"**Region:** {guild.preferred_locale}"
            ),
            inline=False
        )
        
        embed.add_field(
            name="👥 Members",
            value=(
                f"**Tổng:** {total_members}\n"
                f"**Người:** {humans}\n"
                f"**Bots:** {bots}\n"
                f"**Online:** {online_members}"
            ),
            inline=True
        )
        
        embed.add_field(
            name="📚 Channels",
            value=(
                f"**Text:** {text_channels}\n"
                f"**Voice:** {voice_channels}\n"
                f"**Roles:** {roles}\n"
                f"**Emojis:** {len(guild.emojis)}"
            ),
            inline=True
        )
        
        embed.add_field(
            name="🌟 Boost",
            value=(
                f"**Level:** {boost_level}\n"
                f"**Boosts:** {boost_count}\n"
                f"**Max Members:** {guild.max_members}\n"
                f"**Verification:** {guild.verification_level}"
            ),
            inline=True
        )
        
        embed.set_footer(text=f"FLARE AI • {guild.name}")
        await ctx.send(embed=embed)
    
    # ==================== USER INFO ====================
    
    @commands.command(name="userinfo", aliases=["ui", "user", "whois"])
    async def user_info(self, ctx: commands.Context, member: discord.Member = None):
        """
        Hiển thị thông tin chi tiết về user
        
        Cách dùng: 
        • !userinfo - Xem thông tin của bạn
        • !userinfo @user - Xem thông tin user khác
        
        Ví dụ: !userinfo @FlareDev
        """
        # Nếu không mention ai thì lấy chính mình
        if member is None:
            member = ctx.author
        
        # Tính ngày tham gia
        created_at = member.created_at.strftime("%d/%m/%Y")
        joined_at = member.joined_at.strftime("%d/%m/%Y") if member.joined_at else "N/A"
        
        # Tính tuổi account
        account_age = (datetime.utcnow() - member.created_at).days
        
        # Roles
        roles = [role.mention for role in member.roles[1:]]  # Bỏ @everyone
        roles_str = ", ".join(roles) if roles else "Không có role"
        if len(roles_str) > 500:
            roles_str = roles_str[:497] + "..."
        
        # Status
        status_map = {
            discord.Status.online: "🟢 Online",
            discord.Status.idle: "🟡 Idle",
            discord.Status.dnd: "🔴 Do Not Disturb",
            discord.Status.offline: "⚫ Offline"
        }
        status = status_map.get(member.status, "Unknown")
        
        # Badges
        badges = []
        if member.public_flags:
            flags = member.public_flags
            if flags.staff: badges.append("👨‍💼 Staff")
            if flags.partner: badges.append("🤝 Partner")
            if flags.bug_hunter: badges.append("🐛 Bug Hunter")
            if flags.early_supporter: badges.append("🌟 Early Supporter")
            if flags.verified_bot_developer: badges.append("🤖 Bot Dev")
        badges_str = ", ".join(badges) if badges else "Không có"
        
        embed = discord.Embed(
            title=f"👤 {member.display_name} - User Info",
            color=member.color if member.color != discord.Color.default() else config.bot.color,
            timestamp=datetime.utcnow()
        )
        
        if member.display_avatar:
            embed.set_thumbnail(url=member.display_avatar.url)
        
        embed.add_field(
            name="📌 Thông Tin Cơ Bản",
            value=(
                f"**Tên:** {member.name}\n"
                f"**Display Name:** {member.display_name}\n"
                f"**ID:** `{member.id}`\n"
                f"**Bot:** {'✅' if member.bot else '❌'}\n"
                f"**Status:** {status}"
            ),
            inline=False
        )
        
        embed.add_field(
            name="📅 Thời Gian",
            value=(
                f"**Tạo Account:** {created_at}\n"
                f"**Tham Gia Server:** {joined_at}\n"
                f"**Tuổi Account:** {account_age} ngày"
            ),
            inline=True
        )
        
        embed.add_field(
            name="🏷️ Thông Tin Khác",
            value=(
                f"**Top Role:** {member.top_role.mention if member.top_role else 'N/A'}\n"
                f"**Roles:** {len(member.roles)} roles\n"
                f"**Badges:** {badges_str}"
            ),
            inline=True
        )
        
        embed.set_footer(text=f"FLARE AI • {member.name}")
        await ctx.send(embed=embed)
    
    # ==================== AVATAR ====================
    
    @commands.command(name="avatar", aliases=["ava", "avt", "pfp"])
    async def avatar(self, ctx: commands.Context, member: discord.Member = None):
        """
        Xem avatar của user
        
        Cách dùng:
        • !avatar - Xem avatar của bạn
        • !avatar @user - Xem avatar user khác
        
        Ví dụ: !avatar @FlareDev
        """
        if member is None:
            member = ctx.author
        
        # Lấy avatar URL (size 4096 là max)
        avatar_url = member.display_avatar.url.replace("size=1024", "size=4096")
        
        embed = discord.Embed(
            title=f"🖼️ Avatar của {member.display_name}",
            color=member.color if member.color != discord.Color.default() else config.bot.color,
            timestamp=datetime.utcnow()
        )
        
        embed.set_image(url=avatar_url)
        
        # Thêm links tải
        embed.add_field(
            name="🔗 Links Tải",
            value=(
                f"[PNG]({avatar_url}) • "
                f"[JPG]({avatar_url.replace('webp', 'jpg')})"
            ),
            inline=False
        )
        
        embed.set_footer(text="Click vào ảnh để xem full size")
        await ctx.send(embed=embed)
    
    # ==================== INVITE ====================
    
    @commands.command(name="invite", aliases=["mời", "link", "addbot"])
    async def invite(self, ctx: commands.Context):
        """
        Lấy link mời FLARE AI vào server của bạn
        
        Cách dùng: !invite
        """
        invite_url = (
            f"https://discord.com/oauth2/authorize"
            f"?client_id={self.bot.user.id}"
            f"&permissions=2147485696"
            f"&scope=bot%20applications.commands"
        )
        
        embed = discord.Embed(
            title="🌟 Mời FLARE AI Vào Server!",
            description=(
                f"Cảm ơn bạn đã quan tâm đến **{config.bot.name}**!\n\n"
                f"**👉 [Click Here để mời bot]({invite_url})**\n\n"
                f"**Quyền cần thiết:**\n"
                f"• Đọc và gửi tin nhắn\n"
                f"• Đọc lịch sử tin nhắn\n"
                f"• Embed links\n"
                f"• Attach files\n\n"
                f"**Lưu ý:** Bot cần quyền Administrator hoặc các quyền trên để hoạt động tốt nhất!"
            ),
            color=config.bot.color,
            timestamp=datetime.utcnow()
        )
        
        if self.bot.user.display_avatar:
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        
        embed.set_footer(text="FLARE AI • Miễn phí 100%")
        await ctx.send(embed=embed)
    
    # ==================== SUGGEST ====================
    
    @commands.command(name="suggest", aliases=["góp-ý", "feedback", "idea"])
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def suggest(self, ctx: commands.Context, *, suggestion: str):
        """
        Gửi góp ý/ý tưởng cho đội phát triển FLARE AI
        
        Cách dùng: !suggest <ý tưởng của bạn>
        
        Ví dụ: !suggest Thêm tính năng tạo ảnh AI
        """
        # Tạo embed cho suggestion
        embed = discord.Embed(
            title="💡 Góp Ý Mới",
            description=suggestion[:1000],
            color=0x00ffcc,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="👤 Người Gửi",
            value=(
                f"**User:** {ctx.author.mention}\n"
                f"**ID:** `{ctx.author.id}`\n"
                f"**Server:** {ctx.guild.name if ctx.guild else 'DM'}"
            ),
            inline=False
        )
        
        embed.set_footer(text="FLARE AI Feedback System")
        
        # Gửi feedback
        await ctx.send("✅ **Cảm ơn bạn đã góp ý!** Đội phát triển sẽ xem xét ý kiến của bạn. 🙏", delete_after=10)
        
        # Log feedback (có thể gửi vào channel riêng của dev)
        log.info(f"New suggestion from {ctx.author}: {suggestion[:100]}")
        
        # Nếu có owner, gửi DM cho owner
        owner = self.bot.get_user(config.discord.owner_id)
        if owner:
            try:
                await owner.send(embed=embed)
            except:
                pass
    
    # ==================== HELPER METHODS ====================
    
    def _get_uptime(self) -> str:
        """Tính thời gian uptime"""
        uptime = datetime.utcnow() - self.start_time
        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        parts = []
        if days > 0:
            parts.append(f"{days}d")
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        parts.append(f"{seconds}s")
        
        return " ".join(parts)

# ==================== SETUP ====================

async def setup(bot: commands.Bot):
    """Setup function để load cog"""
    await bot.add_cog(UtilityCommands(bot))
    log.info("✅ Utility Commands loaded đầy đủ!")