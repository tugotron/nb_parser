import os
import logging

from telegram.ext import Updater, CommandHandler
from telegram.error import TelegramError

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
        self.all_ids = self.db.get_ids()

    def stop(self, update, context):
        self.db.remove_id(chat_id=context.message.chat_id)
        self.all_ids = self.db.get_ids()

    def sessions(self, update, context):
        data = self.last_update
        self.updater.bot.send_message(context.message.chat_id, data)

    def worker(self, bot, job):
        new_data = self.parser.get_sessions()

        try:
            if self.last_update != new_data:
                for _id in self.all_ids:
                    self.updater.bot.send_message(_id, new_data)  # job.context.message.reply_text('')
                    self.last_update = new_data
        except TelegramError:
            self.db.remove_id(chat_id=job.context.message.chat_id)
            self.all_ids = self.db.get_ids()

    def start(self, bot, update, job_queue):
        self.db.save(update.message.chat_id)
        self.all_ids = self.db.get_ids()

        job_queue.run_repeating(self.worker, 5, context=update)

    def handlers(self):
        start_handler = CommandHandler('start', self.start, pass_job_queue=True)
        self.dispatcher.add_handler(start_handler)

        stop_handler = CommandHandler('stop', self.stop)
        self.dispatcher.add_handler(stop_handler)

        sessions_handler = CommandHandler('sessions', self.sessions)
        self.dispatcher.add_handler(sessions_handler)

    def run(self):
        self.handlers()

        self.updater.start_polling()
        self.updater.idle()
