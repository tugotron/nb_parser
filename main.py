import requests
from lxml import html

page = requests.get('https://livinginnb.ca/')
tree = html.fromstring(page.content)
e1 = tree.xpath('//*[@id="block-views-show-available-surveys-block"]/div/div/div/table/tbody')[0]


def format_str(string):
    new_str = string.split('-')[0]
    new_str = ', '.join(new_str.split(', ')[-2:])
    return new_str.strip()


for i in e1.getchildren():
    datetime = format_str(i.find('td',
                                 {'class': 'views-field-field-event-date'}).find('span',
                                                                                 {'class': 'date-display-single'}).text)

    location = format_str(i.getchildren()[1].text)

    print(f'{datetime} :: {location}')
