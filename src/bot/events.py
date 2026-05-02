cat > src/bot/events.py << 'ENDOFFILE'
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
        await bot.process_commands(message)
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
                title="FLARE AI - Flare Studios Assistant",
                description=f"**{bot.user.name}** is now online.\nServer: Flare Studios\nPrefix: `{config.discord.prefix}`\nUse `{config.discord.prefix}help` for commands.",
                color=config.bot.color
            )
            await channel.send(embed=embed)
    
    @bot.event
    async def on_command_error(ctx, error):
        if isinstance(error, commands.CommandNotFound):
            await ctx.send(f"Command not found. Use `{config.discord.prefix}help`", delete_after=10)
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"Please wait {error.retry_after:.1f}s", delete_after=10)
        else:
            log.error(f"Error: {error}")

async def handle_dm_message(bot, message):
    async with message.channel.typing():
        response = await ai_handler.get_response(str(message.author.id), message.content, "default")
        if len(response) > 2000:
            for chunk in split_long_message(response):
                await message.reply(chunk)
        else:
            await message.reply(response)

async def handle_mention_message(bot, message):
    content = message.content.replace(f'<@{bot.user.id}>', '').strip()
    if not content:
        await message.reply(f"FLARE AI here. Use `{config.discord.prefix}help` for commands.")
        return
    async with message.channel.typing():
        try:
            with open("data/unlocked_users.json", "r") as f:
                unlocked = json.load(f)
            is_unlocked = message.author.id in unlocked
        except:
            is_unlocked = False
        prompt_type = "mastermind" if is_unlocked else "default"
        response = await ai_handler.get_response(str(message.author.id), content, prompt_type, ctx=message)
        if len(response) > 2000:
            for chunk in split_long_message(response):
                await message.reply(chunk)
        else:
            await message.reply(response)
ENDOFFILE

echo "✅ events.py fixed!"
