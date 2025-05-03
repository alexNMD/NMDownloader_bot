import discord

from config import LOG_LEVEL, DISCORD_TOKEN, BOT_MESSAGES_CHANNEL_ID, PREFIX
from services.bot import NMDownloader

custom_intents = discord.Intents.default()
custom_intents.typing = False
custom_intents.presences = False
custom_intents.message_content = True

client = NMDownloader(
    intents=custom_intents,
    bot_channel=BOT_MESSAGES_CHANNEL_ID,
    command_prefix=PREFIX
)

if __name__ == '__main__':
    client.run(token=DISCORD_TOKEN, log_level=LOG_LEVEL)
