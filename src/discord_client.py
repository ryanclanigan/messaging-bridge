import discord
import asyncio
import io
import aiohttp
import utils

from random_generators import RandomMessageGenerator
from base_client import BaseClient


class DiscordClient(discord.Client, BaseClient):
    def __init__(self, discord_config, send_handler):
        discord.Client.__init__(self)
        self.channel = discord_config.channel_id
        self.token = discord_config.client_token
        self.send_handler = send_handler

    async def on_message(self, message):
        if message.author == self.user:
            return

        if message.channel.id != self.channel:
            return

        try:
            if message.content != None and len(message.content) > 0:
                text = (
                    utils.format_message(
                        message.author.name + RandomMessageGenerator.get_random_said()
                    )
                    + message.content
                )
            else:
                text = None

            if len(message.attachments) > 0:
                urls = [a.url for a in message.attachments]
            else:
                urls = None

            self.send_handler(self.get_client_name(), text, urls)

        except Exception as e:
            print(e)

    async def on_ready(self):
        print("We have logged in as {0.user}".format(self))

    def send_message(self, text=None, urls=None):
        self.loop.create_task(
            self.send_message_in_loop(self.get_channel(self.channel), text, urls)
        )

    async def send_message_in_loop(self, channel, message=None, files=None):
        try:
            if files is not None:
                for file in files:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(file) as resp:
                            if resp.status != 200:
                                return await channel.send("Could not download file...")
                            data = io.BytesIO(await resp.read())
                            await channel.send(
                                file=discord.File(data, "cool_image.png")
                            )

            if message is not None:
                await channel.send(message)
        except Exception as e:
            print(e)

    @staticmethod
    def get_client_name():
        return "Discord"

    def is_threadable(self) -> bool:
        return False

    def run_client(self, *args):
        token = args[0]
        self.run(token)

    def get_run_args(self):
        return self.token
