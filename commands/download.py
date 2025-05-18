from discord.ext import commands

from config import logger
from tasks.download_tasks import download_task

class Download(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="download", aliases=["d"])
    async def handle_download(self, ctx):
        """ USAGE: send link to download file (separate w/ ',') """

        message = ctx.message
        _message_content = message.content.split()
        if len(_message_content) <= 1:
            await message.reply("USAGE: send link to download file (separate w/ ',')")
            return

        link = _message_content[1]
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

    # Cause: Discords Cog command isn't triggered when message is posted from webhook...
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        if message.webhook_id:
            ctx = await self.bot.get_context(message)
            await self.bot.invoke(ctx)

async def setup(bot):
    await bot.add_cog(Download(bot))
