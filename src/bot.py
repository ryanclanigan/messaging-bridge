import threading
import json

from discord_client import DiscordClient
from facebook_client import FacebookClient


class Bridge:
    registered_clients = {}

    def __init__(self, *clients):
        for client in clients:
            Bridge.registered_clients[client.get_client_name()] = client

    def run(self):
        threadables = []
        non_threadables = []
        for _, client in Bridge.registered_clients.items():
            if client.is_threadable():
                threadables.append(client)
            else:
                non_threadables.append(client)

        listeners = []
        for threadable in threadables:
            listener = threading.Thread(
                target=threadable.run_client, args=threadable.get_run_args()
            )

            listeners.append(listener)
            listener.start()

        for non_threadable in non_threadables:
            non_threadable.run_client(non_threadable.get_run_args())

        for listener in listeners:
            listener.join()

        print("This message indicates these threads finished, which is concerning")

    @staticmethod
    def send_handler(name, text, urls):
        for client_name, client in Bridge.registered_clients.items():
            if client_name == name:
                continue

            client.send_message(text, urls)


class Config:
    def __init__(self, j):
        self.__dict__ = json.load(j)


with open("config/discord.json") as dj:
    discord_client = DiscordClient(Config(dj), Bridge.send_handler)

with open("config/facebook.json") as fj:
    facebook_client = FacebookClient(Config(fj), Bridge.send_handler)

bridge = Bridge(discord_client, facebook_client)
bridge.run()
