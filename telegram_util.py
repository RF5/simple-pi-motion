import telegram
import json
import time
from telegram.ext import MessageHandler, CommandHandler

chat_id = json.loads(open('./bot_info.json', 'r').read())['my_chat_id'] # hard-code the chat_id of the bot and your phone

class TelegramManager(object):

    def __init__(self, token):
        self.updater = telegram.ext.Updater(token=token)
        self.bot = self.updater.bot

    def ping(self):
        self.bot.send_message(chat_id=chat_id, text="Ping test")

    def send_video(self):
        self.bot.send_video(chat_id=chat_id, video=open('output.mp4', 'rb'), supports_streaming=True)
        print("Video(s) sent!")

    def link_function(self, keyword, func):
        dispatcher = self.updater.dispatcher
        link_handler = CommandHandler(keyword, func, pass_args=True)
        dispatcher.add_handler(link_handler)