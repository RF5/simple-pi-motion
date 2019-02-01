import telegram
import json
import time, os
from telegram.ext import MessageHandler, CommandHandler
from pathlib import Path

dir_path = Path(os.path.dirname(os.path.realpath(__file__)))

class TelegramManager(object):
    def __init__(self, bot_info):
        self.updater = telegram.ext.Updater(token=bot_info['token'])
        self.chat_id = bot_info['my_chat_id'] # hard-code the chat_id of the bot and your phone
        self.bot = self.updater.bot

    def ping(self):
        self.bot.send_message(chat_id=self.chat_id, text="Ping test")

    def send_video(self):
        self.bot.send_video(chat_id=self.chat_id, video=open(dir_path/'output.mp4', 'rb'), supports_streaming=True)
        print("Video(s) sent!")

    def link_function(self, keyword, func):
        dispatcher = self.updater.dispatcher
        link_handler = CommandHandler(keyword, func, pass_args=True)
        dispatcher.add_handler(link_handler)