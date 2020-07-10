import fbchat
import getpass
import discord
import threading 
import json
import asyncio

bot_prefix = '$$'

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

    if not hasattr(self, 'fb_client'):
      return

    if not message.content.startswith(bot_prefix):
      new_message = fbchat.Message(text=bot_prefix + message.author.name + ' said: ' + message.content)
      try:
        response = self.fb_client.send(new_message, thread_id=self.fb_client.thread_id, thread_type=self.fb_client.thread_type)
        print(response)
      except Exception as e:
        print(e)

  async def on_ready(self):
    print('We have logged in as {0.user}'.format(self))        


class FacebookClient(fbchat.Client):
  def __init__(self, facebook_config):
    cookies = {}
    try:
      # Load the session cookies
      with open('session.json', 'r') as f:
          cookies = json.load(f)
    except:
      # If it fails, never mind, we'll just login again
      pass
    
    fbchat.Client.__init__(self, facebook_config.email, facebook_config.password, session_cookies=cookies, user_agent='Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6')

    self.thread_id = facebook_config.group_id
    self.thread_type = fbchat.ThreadType.GROUP
    self.cookies = cookies
    self.email = facebook_config.email
    self.password = facebook_config.password

    with open('session.json', 'w') as f:
      json.dump(self.getSession(), f)

  def set_discord_client(self, discord_client):
    self.discord_client = discord_client

  async def send_message(self, channel, message):
    try:
      response = await channel.send(message)
      print(response)
    except Exception as e:
      print(e)

  def onMessage(self, author_id, message_object, thread_id, thread_type, **kwargs):
    if not self.isLoggedIn():
      self.login(self.email, self.password)
      with open('session.json', 'w') as f:
        json.dump(self.getSession(), f)

    if thread_id != self.thread_id: 
      return

    if not hasattr(self, 'discord_client') or self.discord_client == None:
      return

    if not message_object.text.startswith(bot_prefix):
      user = self.fetchUserInfo(author_id)[author_id]
      message = bot_prefix + user.name + ' said: ' + message_object.text
      channel = self.discord_client.get_channel(self.discord_client.channel)
      self.discord_client.loop.create_task(self.send_message(channel, message))

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

with open('config/discord.json') as dj:
  discord_config = Config(dj)

with open('config/facebook.json') as fj:
  facebook_config = Config(fj)

bridge = Bridge(discord_config, facebook_config)
bridge.run(discord_config.client_token)