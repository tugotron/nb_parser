import requests
from lxml import html


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
        return res or 'No sessions'

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
