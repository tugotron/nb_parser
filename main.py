import time
import os
import logging
import requests
from lxml import html
from telegram.ext import Updater, CommandHandler


def format_str(string):
    new_str = string.split('-')[0]
    new_str = ', '.join(new_str.split(', ')[-2:])
    return new_str.strip()


def format_message(arr):
    res = ''
    for k in arr:
        res += f'{k}\n'
        res += '\n'.join([f'▫️ {v}' for v in arr[k]])
        res += '\n\n'
    return res


def get_sessions():
    page = requests.get('https://livinginnb.ca/')
    tree = html.fromstring(page.content)
    elements = tree.xpath('//*[@id="block-views-show-available-surveys-block"]/div/div/div/table/tbody')[0]
    result = {}
    for i in elements.getchildren():
        datetime = format_str(i.find('td', {'class': 'views-field-field-event-date'}).find('span',
                                                        {'class': 'date-display-single'}).text)
        location = format_str(i.getchildren()[1].text)

        # get detailed info
        link = i.getchildren()[2].find('a').get('href')
        details_page = requests.get(link)
        details_tree = html.fromstring(details_page.text)
        li = [li.text_content() for li in details_tree.cssselect('div[id=block-system-main] ul li')]

        result[f'{datetime} - {location}'] = li

    return result


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


def start(update, context):
    update.send_message(update.message.chat_id, 'Hi!')  # todo: send the list of current sessions


updater = Updater(token=os.environ['BOT_TOKEN'])
dispatcher = updater.dispatcher

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)
updater.start_polling()
updater.idle()


# def main():
#     pass
#
#
# if __name__ == '__main__':
#     try:
#         main()
#     except KeyboardInterrupt:
#         exit()
