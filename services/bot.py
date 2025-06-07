from discord.ext import commands

from config import logger, ENV


class NMDownloader(commands.Bot):
    def __init__(self, bot_channel, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bot_channel = bot_channel

    async def setup_hook(self):
        await self.load_extension("commands.download")

    async def on_ready(self):
        bot_messages_channel = self.get_channel(self.bot_channel)
        if ENV != "DEV":
            await bot_messages_channel.send(f"{self.user} connected")
        logger.info(f"Logged in as {self.user}")
