import discord
import fbchat

from random_generators import RandomMessageGenerator


class DiscordClient(discord.Client):
    def __init__(self, discord_config):
        discord.Client.__init__(self)
        self.channel = discord_config.channel_id

    def set_fb_client(self, fb_client):
        self.fb_client = fb_client

    async def on_message(self, message):
        if message.author == self.user:
            return

        if message.channel.id != self.channel:
            return

        if not hasattr(self, "fb_client"):
            return

        try:
            if message.content != None and len(message.content) > 0:
                new_message = fbchat.Message(
                    text=message.author.name
                    + RandomMessageGenerator.get_random_said()
                    + message.content
                )
                self.fb_client.send(
                    new_message,
                    thread_id=self.fb_client.thread_id,
                    thread_type=self.fb_client.thread_type,
                )

            if len(message.attachments) > 0:
                for attachment in message.attachments:
                    self.fb_client.sendRemoteImage(
                        attachment.url,
                        message=fbchat.Message(),
                        thread_id=self.fb_client.thread_id,
                        thread_type=self.fb_client.thread_type,
                    )

        except Exception as e:
            print(e)

    async def on_ready(self):
        print("We have logged in as {0.user}".format(self))
