import json
import asyncio
import io
import aiohttp
import fbchat
import discord

from random_generators import RandomMessageGenerator
from base_client import BaseClient


class FacebookClient(fbchat.Client, BaseClient):
    def __init__(self, facebook_config, send_handler):
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
        self.send_handler = send_handler

        with open("session.json", "w") as f:
            json.dump(self.getSession(), f)

    def onMessage(self, author_id, message_object, thread_id, thread_type, **kwargs):
        if not self.isLoggedIn():
            self.login(self.email, self.password)
            with open("session.json", "w") as f:
                json.dump(self.getSession(), f)

        if author_id == self.uid:
            return

        if thread_id != self.thread_id:
            return

        user = self.fetchUserInfo(author_id)[author_id]

        if message_object.text is not None:
            text = (
                user.name
                + RandomMessageGenerator.get_random_said()
                + message_object.text
            )
        else:
            text = None

        urls = [
            self.fetchImageUrl(f.uid)
            for f in filter(
                lambda x: not isinstance(x, fbchat.ShareAttachment),
                message_object.attachments,
            )
        ]

        if urls == []:
            urls = None

        self.send_handler(self.get_client_name(), text, urls)

    def send_message(self, text=None, urls=None):
        if text is not None:
            self.send(
                fbchat.Message(text=text),
                thread_id=self.thread_id,
                thread_type=self.thread_type,
            )

        if urls is not None:
            for url in urls:
                self.sendRemoteImage(
                    url,
                    message=fbchat.Message(),
                    thread_id=self.thread_id,
                    thread_type=self.thread_type,
                )

    @staticmethod
    def get_client_name():
        return "Facebook"

    def is_threadable(self) -> bool:
        return True

    def run_client(self, *args):
        self.listen()

    def get_run_args(self):
        return ()
