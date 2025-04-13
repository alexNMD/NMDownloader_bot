import discord
import requests

from urllib.parse import urlparse

from config import logger, ENV, ADMINS, PREFIX, DOWNLOAD_TOKEN
from celery_tasks import start_download


class NMDownloader(discord.Client):
    def __init__(self, bot_channel, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bot_channel = bot_channel

    @staticmethod
    def _get_download_url(links: list):
        """ return santitarized url for download purpose """
        for link in links:
            url = link.split("&")[0]
            if not urlparse(url).netloc == "1fichier.com":
                yield url
            else:
                token_response = requests.post(
                    "https://api.1fichier.com/v1/download/get_token.cgi",
                    json=dict(url=url),
                    headers={"Authorization": f"Bearer {DOWNLOAD_TOKEN}", "Content-Type": "application/json"}
                )
                if not token_response.ok:
                    logger.error(f'get_token failed: {link} - {token_response.content}.')
                    raise Exception(f'get_token failed: {link} - {token_response.content}.')

                download_dct = token_response.json()
                ready_url = download_dct.get('url')
                logger.info(f"Ready to download: {ready_url}")
                yield ready_url

    async def on_ready(self):
        bot_messages_channel = self.get_channel(self.bot_channel)
        if ENV != "DEV":
            await bot_messages_channel.send(f"{self.user} connected")
        logger.info(f'Logged in as {self.user}')

    async def on_message(self, message):
        if message.author == self.user:
            return

        if str(message.author) not in ADMINS:
            logger.warning(f"User Unauthorized: {message.author}")
            await message.reply("User Unauthorized")
            return

        if message.content.startswith((f'{PREFIX}download', f'{PREFIX}d')):
            message_content = message.content.split()
            link = message_content[1] if len(message_content) > 1 else ""
            links = link.split(",")

            try:
                for url in self._get_download_url(links):
                    task = start_download.delay(
                        url=url,
                        message_id=message.id,
                        channel_id=message.channel.id
                    )
                    logger.info(f'Task sent: {task.id}')
            except Exception as download_error:
                logger.error(f'download failed. Error: {download_error}')
                await message.reply(f'download failed. Error: {download_error}')
                return
