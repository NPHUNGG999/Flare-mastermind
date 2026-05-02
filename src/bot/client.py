cat > src/bot/client.py << 'ENDOFFILE'
import discord
from discord.ext import commands
from typing import Optional
from datetime import datetime
from ..utils.config import config
from ..utils.logger import get_logger

log = get_logger(__name__)

class FlareBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.messages = True
        intents.guilds = True
        intents.members = True
        
        super().__init__(
            command_prefix=config.discord.prefix,
            intents=intents,
            help_command=None,
            case_insensitive=True,
            owner_id=config.discord.owner_id
        )
        
        self.config = config
        self.start_time = None
    
    async def setup_hook(self) -> None:
        log.info("Loading extensions...")
        extensions = [
            "src.commands.ai_commands",
            "src.commands.code_commands",
            "src.commands.utility_commands"
        ]
        for ext in extensions:
            try:
                await self.load_extension(ext)
                log.info(f"  Loaded: {ext}")
            except Exception as e:
                log.error(f"  Failed: {ext} - {e}")
        log.info("All extensions loaded!")
    
    async def on_ready(self):
        self.start_time = datetime.utcnow()
        log.info(f"{self.user.name} is ready!")
        log.info(f"ID: {self.user.id}")
        log.info(f"Servers: {len(self.guilds)}")
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name=f"{config.discord.prefix}help | Flare Studios"
            )
        )
        print(f"FLARE AI Online | Servers: {len(self.guilds)} | Users: {len(self.users)}")
    
    def run_bot(self):
        if not config.validate():
            raise ValueError("Configuration invalid! Check .env file")
        super().run(config.discord.token, log_handler=None)
ENDOFFILE

echo "✅ client.py fixed!"
