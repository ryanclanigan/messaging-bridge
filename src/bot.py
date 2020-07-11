import threading
import json

from discord_client import DiscordClient
from facebook_client import FacebookClient

class Bridge:
    def __init__(self, discord_config, facebook_config):
        self.discord_client = DiscordClient(discord_config)
        self.facebook_client = FacebookClient(facebook_config)
        self.discord_client.set_fb_client(self.facebook_client)
        self.facebook_client.set_discord_client(self.discord_client)

    def run(self, discord_token):
        facebook_listener = threading.Thread(target=self.facebook_client.listen)
        facebook_listener.start()

        self.discord_client.run(discord_token)

        facebook_listener.join()

        print("This message indicates these threads finished, which is concerning")


class Config:
    def __init__(self, j):
        self.__dict__ = json.load(j)


with open("config/discord.json") as dj:
    discord_config = Config(dj)

with open("config/facebook.json") as fj:
    facebook_config = Config(fj)

bridge = Bridge(discord_config, facebook_config)
bridge.run(discord_config.client_token)
