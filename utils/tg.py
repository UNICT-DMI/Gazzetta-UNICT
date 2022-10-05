import json
from typing import List, Union
from urllib.parse import unquote
import requests
import yaml

class TelegramBot:
    def __init__(self, token: str, chat_id: Union[int, str], dev_chat_ids: List[str]) -> None:
        self.token = token
        self.chat_id = chat_id
        self.dev_ids = dev_chat_ids
        pass

    @classmethod
    def from_settings_file (cls, filename: str) -> 'TelegramBot':
        with open(filename) as f:
            data = yaml.load(f, Loader=yaml.SafeLoader)
            token, chat_id, dev_chat_ids = data.values()
        return cls(token, chat_id, dev_chat_ids)

    def send_https_request (self, URL: str, params = None, files = None) -> None:
        r = requests.post(URL, params = params, files = files)
        responseJSON = r.json()
        if responseJSON["ok"] == False:
            raise ValueError (json.dumps(responseJSON, indent=2))

    def send_telegram_message(self, text: str, notification: bool, chat_id: Union[str, int] = None) -> None:
        if chat_id == None:
            chat_id = self.chat_id
        params = {
            'chat_id': chat_id,
            'parse_mode': 'markdown',
            'disable_notification': notification,
            'text': text
        }
        URL = "https://api.telegram.org/bot" + self.token + "/sendMessage"
        self.send_https_request(URL, params)

    def send_single_telegram_attachment_by_link(self, pdf_link: str, notification: bool, caption: str = '') -> None:
        params = {
            'chat_id': self.chat_id,
            'caption': caption,
            'parse_mode': 'markdown',
            'disable_notification': notification,
            'document': pdf_link
        }
        URL = "https://api.telegram.org/bot" + self.token + "/sendDocument"
        self.send_https_request(URL, params)

    def send_single_telegram_attachment_by_file(self, pdf_file: str, notification: bool, caption: str = '') -> None:
        notification = notification and caption != ''
        params = {
            'chat_id': self.chat_id,
            'caption': caption,
            'parse_mode': 'markdown',
            'disable_notification': notification,
            'document': 'attach://' + pdf_file.split('/')[-1] 
        }
        file = {pdf_file.split('/')[-1]: open(pdf_file, 'rb')}
        URL = "https://api.telegram.org/bot" + self.token + "/sendDocument"
        self.send_https_request(URL, params, file)

    def send_multiple_telegram_attachments_by_link(self, pdf_links: List[str]) -> None:
        input_media_documents = [ {   "type": "document",  "media": pdf_link   }  for pdf_link in pdf_links]
        params = {
            'chat_id': self.chat_id,
            'disable_notification': True,
            'media': json.dumps(input_media_documents),
        }
        URL = "https://api.telegram.org/bot" + self.token + "/sendMediaGroup"
        self.send_https_request(URL, params)
    
    def send_multiple_telegram_attachments_by_file(self, pdf_files: List[str]) -> None:
        input_media_documents = [ {   "type": "document",  "media": "attach://" + pdf_file.split('/')[-1]   } for pdf_file in pdf_files]
        files = { pdf_file.split('/')[-1]: open(pdf_file, 'rb') for pdf_file in pdf_files }
        params = {
            'chat_id': self.chat_id,
            'disable_notification': True,
            'media': json.dumps(input_media_documents),
        }
        URL = "https://api.telegram.org/bot" + self.token + "/sendMediaGroup"
        self.send_https_request(URL, params, files)

    def send_telegram_announcements(self, pdf_files: List[str], message: str,  notification: bool) -> None:
        try: 
            if len(pdf_files) == 1:
                if len(message) < 1024: 
                    self.send_single_telegram_attachment_by_file(pdf_files[0], notification, message)
                else:
                    self.send_single_telegram_attachment_by_file(pdf_files[0], notification)
                    self.send_telegram_message(message, notification)
            elif len(pdf_files) == 0:
                self.send_telegram_message(message, notification)
            else:
                self.send_multiple_telegram_attachments_by_file(pdf_files)
                self.send_telegram_message(message, notification)
        except:
            self.send_telegram_message(message, notification)

    
    def send_documents_error_message(self, err: ValueError) -> None:
        decoded_url = json.dumps(unquote(err.args[1]))
        #document_list = re.findall(r"https?:.+?(?=\\|\")", decoded_url)
        error_string = "```response sent: " + err.args[0] + "\n```"# + "related documents:\n" + escape_char('\n'.join(document_list))
        #print (json.dumps(unquote(err.args[1])))
        self.send_debug_messages(error_string)

    def send_debug_messages(self, message: str) -> None:
        for dev in self.dev_ids:
            self.send_telegram_message(message, True, dev)
