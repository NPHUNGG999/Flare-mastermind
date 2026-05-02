import discord
from discord.ext import commands
import json
from ..utils.logger import get_logger
from ..utils.config import config
from ..utils.helpers import split_long_message, create_embed
from ..ai.gemini_handler import GeminiHandler
from ..ai.conversation import ConversationManager

log = get_logger(__name__)
ai_handler = GeminiHandler()
conversation_manager = ConversationManager()

def setup_events(bot: commands.Bot):
    
    @bot.event
    async def on_message(message: discord.Message):
        if message.author == bot.user:
            return
        
        ctx = await bot.get_context(message)
        
        if ctx.valid:
            await bot.process_commands(message)
            return
        
        if isinstance(message.channel, discord.DMChannel):
            await handle_dm_message(bot, message)
            return
        
        if bot.user in message.mentions:
            await handle_mention_message(bot, message)
    
    @bot.event
    async def on_guild_join(guild: discord.Guild):
        log.info(f"Joined server: {guild.name}")
        channel = guild.system_channel or next((c for c in guild.text_channels if c.permissions_for(guild.me).send_messages), None)
        if channel:
            embed = create_embed(
                title="FLARE AI",
                description=f"Bot da san sang hoat dong.\nPrefix: `{config.discord.prefix}`\nDung `{config.discord.prefix}help` de xem danh sach lenh.",
                color=config.bot.color
            )
            await channel.send(embed=embed)
    
    @bot.event
    async def on_guild_remove(guild: discord.Guild):
        log.info(f"Left server: {guild.name}")
    
    @bot.event
    async def on_member_join(member: discord.Member):
        log.info(f"Member joined: {member.name} in {member.guild.name}")
    
    @bot.event
    async def on_member_remove(member: discord.Member):
        log.info(f"Member left: {member.name} from {member.guild.name}")
    
    @bot.event
    async def on_command_error(ctx, error):
        if isinstance(error, commands.CommandNotFound):
            return
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("Ban khong co quyen dung lenh nay.", delete_after=10)
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"Vui long doi {error.retry_after:.1f}s truoc khi dung lai.", delete_after=5)
        else:
            log.error(f"Command error: {error}")

async def handle_dm_message(bot, message):
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
            log.error(f"DM error: {e}")
            await message.reply("Co loi xay ra. Vui long thu lai sau.")

async def handle_mention_message(bot, message):
    content = message.content.replace(f'<@{bot.user.id}>', '').strip()
    
    if not content:
        await message.reply(f"FLARE AI day. Dung `{config.discord.prefix}help` de xem lenh.")
        return
    
    async with message.channel.typing():
        try:
            with open("data/unlocked_users.json", "r") as f:
                unlocked = json.load(f)
            is_unlocked = message.author.id in unlocked
        except:
            is_unlocked = False
        
        prompt_type = "mastermind" if is_unlocked else "default"
        
        try:
            response = await ai_handler.get_response(
                user_id=str(message.author.id),
                message=content,
                prompt_type=prompt_type,
                ctx=message
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
            log.error(f"Mention error: {e}")
            await message.reply("Co loi xay ra. Vui long thu lai sau.")
