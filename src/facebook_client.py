import json
import asyncio
import io
import aiohttp
import fbchat
import discord

from random_generators import RandomMessageGenerator


class FacebookClient(fbchat.Client):
    def __init__(self, facebook_config):
        cookies = {}
        try:
            # Load the session cookies
            with open("session.json", "r") as f:
                cookies = json.load(f)
        except:
            # If it fails, never mind, we'll just login again
            pass

        fbchat.Client.__init__(
            self,
            facebook_config.email,
            facebook_config.password,
            session_cookies=cookies,
            user_agent="Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
        )

        self.thread_id = facebook_config.group_id
        self.thread_type = fbchat.ThreadType.GROUP
        self.cookies = cookies
        self.email = facebook_config.email
        self.password = facebook_config.password

        with open("session.json", "w") as f:
            json.dump(self.getSession(), f)

    def set_discord_client(self, discord_client):
        self.discord_client = discord_client

    async def send_message(self, channel, message=None, files=None):
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

    def onMessage(self, author_id, message_object, thread_id, thread_type, **kwargs):
        if not self.isLoggedIn():
            self.login(self.email, self.password)
            with open("session.json", "w") as f:
                json.dump(self.getSession(), f)

        if author_id == self.uid:
            return

        if thread_id != self.thread_id:
            return

        if not hasattr(self, "discord_client") or self.discord_client == None:
            return

        user = self.fetchUserInfo(author_id)[author_id]
        channel = self.discord_client.get_channel(self.discord_client.channel)

        if message_object.text is not None:
            message = (
                user.name
                + RandomMessageGenerator.get_random_said()
                + message_object.text
            )
        else:
            message = None

        if len(message_object.attachments) > 0:
            files = [self.fetchImageUrl(f.uid) for f in message_object.attachments]
        else:
            files = None

        self.discord_client.loop.create_task(self.send_message(channel, message, files))
