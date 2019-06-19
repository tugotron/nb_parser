import os
import logging
from telegram.ext import Updater, CommandHandler

from .parser import Parser
from .db import Gateway

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


class Bot:
    def __init__(self):
        self.updater = Updater(token=os.environ['BOT_TOKEN'])
        self.dispatcher = self.updater.dispatcher
        self.parser = Parser()
        self.last_update = self.parser.get_sessions()
        self.db = Gateway()

    def save_id(self, user_id):
        self.db.save(user_id)

    def get_ids(self):
        return self.db.get_ids()

    def help(self, update, context):
        pass

    def sessions(self, update, context):
        data = self.last_update
        self.updater.bot.send_message(context.message.chat_id, data)

    def worker(self, bot, job):
        new_data = self.parser.get_sessions()
        chat_id = job.context.message.chat_id
        self.db.save(chat_id)
        if self.last_update != new_data:
            for _id in self.db.get_ids():
                self.updater.bot.send_message(_id, new_data)  # job.context.message.reply_text('')

    def start(self, bot, update, job_queue):
        job_queue.run_repeating(self.worker, 5, context=update)

    def stop(self, user_id):
        self.db.remove_id(user_id)

    def handlers(self):
        start_handler = CommandHandler('start', self.start, pass_job_queue=True)
        self.dispatcher.add_handler(start_handler)

        help_handler = CommandHandler('help', self.help)
        self.dispatcher.add_handler(help_handler)

        sessions_handler = CommandHandler('sessions', self.sessions)
        self.dispatcher.add_handler(sessions_handler)

    def run(self):
        self.handlers()

        self.updater.start_polling()
        self.updater.idle()
