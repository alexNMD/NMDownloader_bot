from discord.ext import commands

from config import logger
from tasks.download_tasks import download_task

class Download(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="download", aliases=["d"])
    async def handle_download(self, ctx):
        message = ctx.message
        _message_content = message.content.split()
        link = _message_content[1] if len(_message_content) > 1 else ""
        _links = link.split(",")

        try:
            for url in _links:
                task = download_task.delay(
                    url=url,
                    message_id=message.id,
                    channel_id=message.channel.id
                )
                logger.info(f'Task sent: {task.id}')
        except Exception as download_error:
            logger.error(f'download failed. Error: {download_error}')
            await message.reply(f'download failed. Error: {download_error}')
        return

async def setup(bot):
    await bot.add_cog(Download(bot))
