from ast import Dict
import traceback
from typing import List, Union
from urllib.parse import urljoin
from bs4 import BeautifulSoup, NavigableString
import requests
from utils.formatting import escape_char, format_dumb_site_text, get_formatted_message
from utils.resources import get_pdf_text, match_regex_tag, save_attachments
import pdfkit


from utils.tg import TelegramBot

class Site:
    def __init__(self, name: str, link: str, token: str, chat_id: Union[int, str], dev_chat_ids: List[str]) -> None:
        self.name = name
        self.link = link
        self.bot = TelegramBot(token, chat_id, dev_chat_ids)
        pass

    def get_main_page(self) -> requests.Response:
        try:
            self.page = requests.get(self.link, timeout=None)
        except requests.exceptions.SSLError:
            self.page = requests.get(self.link, timeout=None)

        if self.page.status_code != 200:
            print("Impossibile accedere al sito di " + self.name + ", riprovare più tardi")
            raise Exception("Impossibile accedere al sito di " + self.name + ", controllare stato codice " + str(self.page.status_code))
        return self.page

    def get_table(self) -> NavigableString:
        soup = BeautifulSoup(self.page.content, 'html5lib')
        self.table = soup.find_all('table')[1]
        return self.table

    def get_headers(self) -> NavigableString:
        self.thead = self.table.find('tr')
        header_cells = self.thead.find_all("td") if self.thead.find_all("td") != [] else self.thead.find_all("th")
        self.headers = [format_dumb_site_text(header.getText()) for header in header_cells]
        if '' in self.headers:
            self.headers.remove('')
        return self.thead.find_next('tr')

    def get_pdf_report(self, td: NavigableString) -> List[str]:
        a_attachments = td.find_all('a')
        link_to_attachment = urljoin (self.link, a_attachments[0]['href'])
        return save_attachments([link_to_attachment])

    def get_asp_pdf(self, td: NavigableString, filename: str) -> List[str]:

        id = td.find_all('input')[0]['value']
        index = "1234567890"
        x = "1234567890"
        y = "1234567890"

        payload='id=' + id + '&oocc=' + index + '&x=' + x + '&y=' + y
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Host': 'www.oocc.unict.it'
        }

        modifier = ("_agg" if filename == "odgagg.pdf" else "")

        response = requests.request("POST", "https://www.oocc.unict.it/oocc/vispubb" + modifier + ".asp", headers=headers, data=payload)
        pdfkit.from_string(response.text, output_path="tmp/" + filename, options={'enable-local-file-access': False})

        return ["tmp/" + filename]

    def find_next_node(self, node: NavigableString) -> NavigableString:
        return node.find_next_sibling()

    def find_previous_node(self, node: NavigableString) -> NavigableString:
        return node.find_previous_sibling()

    def get_row(self, tr: NavigableString) -> None:
        return tr.find_all('td')

    def send_announcement(self, tr: NavigableString, needs_sending: Dict) -> None:
        row = self.get_row(tr)

        message = get_formatted_message(row, self.headers) 

        message += "\n\n*Sito*: " + escape_char(self.link);

        attachments = []
        tags = []

        if needs_sending['announcement']:
            attachments += self.get_asp_pdf(tr.find_all('td')[2], "odg.pdf")
        if needs_sending['odgagg']:
            attachments += self.get_asp_pdf(tr.find_all('td')[3], "odgagg.pdf")
            tags += ["*[OdG Aggiuntivo]*"]
        if needs_sending['pdf_report']:
            attachments += self.get_pdf_report(tr.find_all('td')[4])
            tags += ["*[Resoconto seduta]*"] 

        pdf_text = get_pdf_text(attachments)

        tags += match_regex_tag(pdf_text + message)

        message =  '\n'.join(tags) + '\n\n' + message

        self.bot.send_telegram_announcements(attachments, message, tags == [])

    def  get_all_announcements(self) -> List[str]:
        announcements = [] 
        self.get_main_page()
        self.get_table()
        pointer = self.get_headers()
        while pointer is not None:
            announcements.append({
                'pointer': pointer, 
                'data': get_announcement_data(pointer)
            })
            pointer = self.find_next_node(pointer)
        return announcements
    
    def handle_error(self, exception: Exception) -> None:
        if type(exception) != requests.exceptions.ConnectionError:
            error_string = "An exception was raised while parsing " + self.name + ":\n" + "`" + traceback.format_exc() +  "`"
            print(error_string)
            self.bot.send_debug_messages(error_string)

        else:
            print("Connection error while parsing " + self.name)
            print("An exception was raised while parsing " + self.name + ":\n" + "`" + traceback.format_exc() +  "`")

#data is a composite dictionary
#["sitename"] -> [list of announcements]
#each announcment is a dictionary with keys: object, date, odg, odgagg, pdf report link, verbale 
def get_announcement_data(pointer: NavigableString) -> Dict:
    row_elements = pointer.find_all_next('td')
    return {
        'object': row_elements[0].getText(),
        'date': row_elements[1].getText(),
        'odg': row_elements[2].find('form') is not None ,
        'odgagg': row_elements[3].find('form') is not None,
        'pdf_report': row_elements[4].find('a') is not None, # else row_elements[4].find('a')['href'],
        'verbale': row_elements[5].find('a') is not None # else row_elements[5].find('a')['href']
    }
