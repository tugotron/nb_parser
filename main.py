import os
import logging
import requests
from lxml import html
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, InlineQueryHandler

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


class Parser:
    def format_header(self, string):
        new_str = string.split('-')[0]
        new_str = ', '.join(new_str.split(', ')[-2:])
        return new_str.strip()

    def format_message(self, arr):
        res = ''
        for k, v in arr.items():
            res += f'▫️ {k} - {v}\n'
            # res += f'{k}\n'
            # res += '\n'.join([f'▫️ {v}' for v in arr[k]])
            # res += '\n\n'
        return res

    def get_sessions(self):
        try:
            page = requests.get('https://livinginnb.ca/', timeout=5)
            page.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print(e)

        result = {}
        tree = html.fromstring(page.content)
        elements = tree.xpath('//*[@id="block-views-show-available-surveys-block"]/div/div/div/table/tbody')[0]
        for i in elements.getchildren():
            datetime = self.format_header(i.find('td', {'class': 'views-field-field-event-date'}).find(
                                                'span', {'class': 'date-display-single'}).text)
            location = self.format_header(i.getchildren()[1].text)

            # get detailed info
            # link = i.getchildren()[2].find('a').get('href')
            # details_page = requests.get(link)
            # details_tree = html.fromstring(details_page.text)
            # li = [li.text_content() for li in details_tree.cssselect('div[id=block-system-main] ul li')]
            # result[f'{datetime} - {location}'] = li

            result[f'{datetime}'] = location

        return self.format_message(result)


class Bot:
    def __init__(self):
        self.updater = Updater(token=os.environ['BOT_TOKEN'])
        self.dispatcher = self.updater.dispatcher
        self.last_update = Parser().get_sessions()

    def start(self, update, context):
        self.updater.bot.send_message(context.message.chat_id, 'start handler')

    def help(self, update, context):
        pass

    def sessions(self, update, context):
        data = self.last_update
        self.updater.bot.send_message(context.message.chat_id, data)

    def time(self, bot, update, job_queue):
        job = job_queue.run_repeating(self.sessions, 5, context=update)

    def handlers(self):
        start_handler = CommandHandler('start', self.start)
        self.dispatcher.add_handler(start_handler)

        help_handler = CommandHandler('help', self.help)
        self.dispatcher.add_handler(help_handler)

        sessions_handler = CommandHandler('sessions', self.sessions)
        self.dispatcher.add_handler(sessions_handler)

        message_handler = CommandHandler('start', self.time, pass_job_queue=True)
        self.dispatcher.add_handler(message_handler)

    def run(self):
        self.handlers()

        self.updater.start_polling()
        # self.updater.idle()


if __name__ == '__main__':
    bot = Bot()
    bot.run()
